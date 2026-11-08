"""Agent loop for QC after a quantms run: diagnose, change a setting, rerun, compare.

This is the one step of the workflow where the next action depends on
interpreting results, so the LLM chooses it. Everything else stays in code:

- QC metrics, flagged channels and run-to-run comparisons are computed by
  code (`quantms_qc.py`) and handed to the model as tool results.
- Every rerun goes through an approval gate (the analyst), and is checked
  before it reaches the gate: only known pipeline parameters, known process
  names and a limited number of reruns and tool calls are allowed.
- When the model finishes, code checks its stated status against the flags
  of the first and last run (e.g. "resolved" while channels are still
  flagged is recorded as a conflict).

Two ways to execute a rerun:

- `ReplayBackend` returns runs that were actually executed and recorded in
  `data/quantms_pxd000001/`. A request that does not reproduce a recorded
  run is refused, and the model is told so. The quantms behaviour it
  reproduces (the `reporter_mass_shift` pipeline parameter is recorded but
  does not reach OpenMS IsobaricWorkflow, so the cached step is reused) was
  observed in quantms 1.10.0; see `examples/quantms_pxd000001_investigation.md`.
- `NextflowBackend` runs quantms with `-resume` and an `ext.args` config.
  It needs Nextflow and Docker and has not been executed in this repository.
"""

from __future__ import annotations

import json
import shlex
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

import pandas as pd

from tmt_agents.design_check import default_model
from tmt_agents.quantms_qc import (
    channel_metrics,
    expected_amounts,
    pooled_slope,
    protein_matrix,
    psm_counts,
    read_msstats_in,
    spike_in_recovery,
)

# Channel flags (deterministic). A channel is flagged if it quantifies fewer
# than half the median number of proteins, or its median intensity is an
# outlier across channels.
MIN_QUANT_FRACTION = 0.5
MEDIAN_Z_LIMIT = 3.0

MAX_RERUNS = 3
MAX_TOOL_CALLS = 15

# quantms process names whose arguments can be changed through ext.args.
KNOWN_PROCESSES = {"ISOBARIC_WORKFLOW"}


# ---------------------------------------------------------------------------
# Runs and QC
# ---------------------------------------------------------------------------

@dataclass
class Run:
    run_id: str
    msstats_path: Path
    params: dict
    command: str  # command of the ISOBARIC_WORKFLOW step
    ext_args: dict[str, str] = field(default_factory=dict)
    note: str = ""    # shown to the model
    source: str = ""  # transcript only (e.g. which recorded run was replayed)


@dataclass
class RunQC:
    metrics: pd.DataFrame
    spikes: pd.DataFrame
    pooled_slope: float | None
    flagged: list[str]


def flag_channels(metrics: pd.DataFrame) -> list[str]:
    med = metrics["n_quantified"].median()
    low = metrics["n_quantified"] < MIN_QUANT_FRACTION * med
    out = metrics["raw_median_z"].abs() > MEDIAN_Z_LIMIT
    return [c for c in metrics.index if low[c] or out[c]]


def compute_qc(run: Run) -> RunQC:
    msstats = read_msstats_in(run.msstats_path)
    y = protein_matrix(msstats)
    per_channel, spikes = spike_in_recovery(y, expected_amounts(msstats), psm_counts(msstats))
    metrics = channel_metrics(y, exclude=[p for p in spikes["protein"] if p])
    found = list(spikes.dropna(subset=["slope"])["accession"])
    slope = pooled_slope(per_channel, found) if found else None
    return RunQC(metrics, spikes, slope, flag_channels(metrics))


def command_tokens(command: str) -> Counter:
    """Arguments of the IsobaricWorkflow call, as a multiset of tokens.

    Only the lines up to the output redirection are used; numbers are
    normalised so that '0.010' and '0.01' compare equal.
    """
    body = command.split("2>&1")[0]
    tokens = [t for t in shlex.split(body.replace("\\\n", " ")) if t not in ("\\", "")]
    norm = []
    for t in tokens:
        try:
            norm.append(repr(float(t)))
        except ValueError:
            norm.append(t)
    return Counter(norm)


def command_diff(a: str, b: str) -> dict:
    ta, tb = command_tokens(a), command_tokens(b)
    return {"removed": sorted((ta - tb).elements()), "added": sorted((tb - ta).elements())}


# ---------------------------------------------------------------------------
# Rerun requests and backends
# ---------------------------------------------------------------------------

@dataclass
class RerunRequest:
    base_run: str
    param_changes: dict
    ext_args: dict[str, str]
    hypothesis: str
    expected_change: str


class Backend(Protocol):
    def initial_run(self) -> Run: ...
    def rerun(self, base: Run, request: RerunRequest, run_id: str) -> Run | str: ...


class ReplayBackend:
    """Serve recorded runs; refuse anything that was not actually executed.

    `recorded` maps each tag to the ext.args the run was made with ({} for a
    run without overrides; exactly one such run is required). For each tag
    the folder must contain msstats_in_<tag>.csv.gz, params_<tag>.json and
    isobaric_command_<tag>.sh.
    """

    # Pipeline parameters observed (quantms 1.10.0) not to change the
    # IsobaricWorkflow command. Changing only these reuses the cached step.
    PARAMS_NOT_PASSED = {"reporter_mass_shift"}
    # IsobaricWorkflow defaults (OpenMS, confirmed with --helphelp). An
    # explicit argument equal to its default gives the same output as no
    # argument, so it is matched to the run without overrides.
    OPENMS_DEFAULTS = {"-extraction:reporter_mass_shift": 0.002}

    def __init__(self, data_dir: Path, initial_tag: str, recorded: dict[str, dict[str, str]]):
        self.data_dir = Path(data_dir)
        self.initial_tag = initial_tag
        self.recorded = {t: self._load(t, t, ext) for t, ext in recorded.items()}
        bare = [t for t, ext in recorded.items() if not ext]
        if len(bare) != 1:
            raise ValueError("exactly one recorded run without ext.args is required")
        self.bare = self.recorded[bare[0]]

    def _load(self, tag: str, run_id: str, ext_args: dict[str, str]) -> Run:
        d = self.data_dir
        params = json.loads((d / f"params_{tag}.json").read_text(encoding="utf-8"))
        params["outdir"] = "results"  # recorded outdir names would hint at the fix
        return Run(
            run_id=run_id,
            msstats_path=d / f"msstats_in_{tag}.csv.gz",
            params=params,
            command=(d / f"isobaric_command_{tag}.sh").read_text(encoding="utf-8"),
            ext_args=dict(ext_args),
            source=f"recorded run '{tag}'",
        )

    def initial_run(self) -> Run:
        rec = self.recorded[self.initial_tag]
        return Run("run0", rec.msstats_path, dict(rec.params), rec.command, dict(rec.ext_args),
                   "first run", rec.source)

    def _effective_tokens(self, extra: str) -> tuple[Counter, list[str]]:
        """Tokens of the extra arguments without those equal to an OpenMS
        default, and the dropped default arguments."""
        toks = shlex.split(extra)
        kept, dropped, i = [], [], 0
        while i < len(toks):
            opt = toks[i]
            if opt in self.OPENMS_DEFAULTS and i + 1 < len(toks):
                try:
                    if float(toks[i + 1]) == self.OPENMS_DEFAULTS[opt]:
                        dropped += toks[i:i + 2]
                        i += 2
                        continue
                except ValueError:
                    pass
            kept.append(opt)
            i += 1
        kept_tokens = command_tokens("IsobaricWorkflow " + " ".join(kept)) - Counter(["IsobaricWorkflow"])
        return kept_tokens, dropped

    def rerun(self, base: Run, request: RerunRequest, run_id: str) -> Run | str:
        unknown = [k for k in request.param_changes if k not in self.PARAMS_NOT_PASSED]
        if unknown:
            return (f"Not available in replay mode: no recorded run changes {unknown}. "
                    "This change would have to be run in live mode.")
        ext_args = {**base.ext_args, **request.ext_args}
        ext_args = {k: v for k, v in ext_args.items() if v.strip()}
        extra = " ".join(ext_args.get("ISOBARIC_WORKFLOW", "").split())
        kept, dropped = self._effective_tokens(extra)
        target = command_tokens(self.bare.command) + kept
        for tag, rec in self.recorded.items():
            if command_tokens(rec.command) == target:
                params = {**base.params, **request.param_changes}
                note = f"rerun of {base.run_id}"
                if ext_args == base.ext_args:
                    note += "; Nextflow reported ISOBARIC_WORKFLOW as cached"
                command = rec.command
                if dropped:  # show explicit default arguments as a live run would
                    command = command.replace("    2>&1", f"    {shlex.join(dropped)} \\\n    2>&1", 1)
                return Run(run_id, rec.msstats_path, params, command, ext_args, note,
                           source=f"replay of recorded run '{tag}'")
        return ("Not available in replay mode: the resulting IsobaricWorkflow command "
                f"(extra arguments: '{extra}') matches no recorded run. "
                "This change would have to be run in live mode.")


class NextflowBackend:
    """Run quantms with Nextflow (-resume). Not executed in this repository."""

    def __init__(self, workdir: Path, initial: Run, pipeline: str = "bigbio/quantms",
                 revision: str = "1.10.0", profile: str = "test_tmt,docker",
                 base_config: str = "process { resourceLimits = [cpus: 2, memory: 7.GB, time: 12.h] }"):
        self.workdir = Path(workdir)
        self._initial = initial
        self.pipeline, self.revision, self.profile = pipeline, revision, profile
        self.base_config = base_config

    def initial_run(self) -> Run:
        return self._initial

    def config_text(self, ext_args: dict[str, str]) -> str:
        lines = [self.base_config, "process {"]
        for proc, args in ext_args.items():
            lines.append(f"    withName: '.*:{proc}' {{ ext.args = {json.dumps(args)} }}")
        lines.append("}")
        return "\n".join(lines) + "\n"

    def command(self, params: dict, config_path: Path, outdir: str) -> list[str]:
        cmd = ["nextflow", "run", self.pipeline, "-r", self.revision, "-profile", self.profile,
               "-resume", "-c", str(config_path), "--outdir", outdir]
        for k, v in params.items():
            cmd += [f"--{k}", str(v).lower() if isinstance(v, bool) else str(v)]
        return cmd

    def rerun(self, base: Run, request: RerunRequest, run_id: str) -> Run | str:
        ext_args = {**base.ext_args, **request.ext_args}
        cfg = self.workdir / f"{run_id}.config"
        cfg.write_text(self.config_text(ext_args), encoding="utf-8")
        outdir = f"results_{run_id}"
        proc = subprocess.run(self.command(request.param_changes, cfg, outdir),
                              cwd=self.workdir, capture_output=True, text=True)
        if proc.returncode != 0:
            return f"Nextflow failed (exit {proc.returncode}): {proc.stderr[-2000:]}"
        out = self.workdir / outdir
        msstats = next(out.glob("quant_tables/*msstats_in.csv"), None)
        params_file = max(out.glob("pipeline_info/params_*.json"), default=None)
        log = subprocess.run(["nextflow", "log", "last", "-f", "name,workdir"],
                             cwd=self.workdir, capture_output=True, text=True).stdout
        task_dir = next((line.split("\t")[1] for line in log.splitlines()
                         if "ISOBARIC_WORKFLOW" in line), None)
        if not (msstats and params_file and task_dir):
            return "Run finished but its MSstats table, parameters or IsobaricWorkflow command were not found."
        command = (Path(task_dir) / ".command.sh").read_text()
        note = f"rerun of {base.run_id}"
        if command_tokens(command) == command_tokens(base.command):
            note += "; ISOBARIC_WORKFLOW command unchanged (cached task reused)"
        return Run(run_id, msstats, json.loads(params_file.read_text()), command, ext_args,
                   note, source=f"live run in {outdir}")


# ---------------------------------------------------------------------------
# Tools offered to the model
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_qc",
        "description": "Computed QC for one run: channel metrics (background proteins), "
                       "spike-in ratio recovery, and the channels flagged by code.",
        "input_schema": {"type": "object", "properties": {"run_id": {"type": "string"}},
                         "required": ["run_id"]},
    },
    {
        "name": "get_run_config",
        "description": "Pipeline parameters (JSON), ext.args overrides and the command of the "
                       "IsobaricWorkflow (quantification) step of one run.",
        "input_schema": {"type": "object", "properties": {"run_id": {"type": "string"}},
                         "required": ["run_id"]},
    },
    {
        "name": "compare_runs",
        "description": "Computed comparison of two runs: per-channel changes, flagged channels, "
                       "changed parameters and changed arguments of the IsobaricWorkflow command.",
        "input_schema": {"type": "object",
                         "properties": {"run_a": {"type": "string"}, "run_b": {"type": "string"}},
                         "required": ["run_a", "run_b"]},
    },
    {
        "name": "request_rerun",
        "description": (
            "Ask to rerun the pipeline from an existing run with ONE change: pipeline parameters "
            "(param_changes, names as in the parameter JSON) and/or extra command-line arguments "
            "for a process (ext_args, e.g. {\"ISOBARIC_WORKFLOW\": \"-option value\"}). The analyst "
            "must approve. State the hypothesis being tested and the expected change in the metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "base_run": {"type": "string"},
                "param_changes": {"type": "object"},
                "ext_args": {"type": "object", "additionalProperties": {"type": "string"}},
                "hypothesis": {"type": "string"},
                "expected_change": {"type": "string"},
            },
            "required": ["base_run", "param_changes", "ext_args", "hypothesis", "expected_change"],
        },
    },
    {
        "name": "finish",
        "description": "End the investigation with a conclusion for the analyst.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["resolved", "unresolved", "no_action_needed"]},
                "final_run": {"type": "string"},
                "diagnosis": {"type": "string"},
                "evidence": {"type": "string", "description": "Values quoted from tool results."},
                "remaining_issues": {"type": "array", "items": {"type": "string"}},
                "next_steps": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["status", "final_run", "diagnosis", "evidence", "remaining_issues",
                         "next_steps"],
        },
    },
]

SYSTEM = (
    "You investigate quality-control problems in a TMT proteomics run processed with the "
    "quantms pipeline. You work through tools; all numbers come from code, and you never "
    "see plots.\n"
    "1. Start with get_qc and get_run_config on run0.\n"
    "2. If channels are flagged or another metric stands out, form hypotheses about the "
    "cause, most likely first, using the metrics, parameters and the quantification command.\n"
    "3. To test a hypothesis you may request a rerun. Change one thing at a time, state the "
    "hypothesis and the expected change, and use as few reruns as possible. The analyst must "
    "approve each rerun; a refused or unavailable rerun is information, not an error.\n"
    "4. After each rerun, use compare_runs to check whether the change did what you expected, "
    "including whether the quantification command actually changed.\n"
    "5. Call finish when the problem is resolved, when no further rerun would be informative, "
    "or when your budget is used. Distinguish what the metrics show from what you infer, and "
    "list remaining issues and checks for the analyst."
)


def format_qc(run: Run, qc: RunQC) -> str:
    return (
        f"Run {run.run_id} ({run.note})\n"
        f"Channel metrics (n_quantified = proteins quantified; raw_median = median log2 "
        f"intensity; raw_median_z = robust z across channels; corr_to_others = correlation "
        f"with the mean of the other channels, NaN if too few complete proteins):\n"
        f"{qc.metrics.to_string()}\n\n"
        f"Flagged by code (n_quantified < {MIN_QUANT_FRACTION} x median, or "
        f"|raw_median_z| > {MEDIAN_Z_LIMIT}): {qc.flagged or 'none'}\n\n"
        f"Spike-in recovery (slope 1 = full recovery):\n{qc.spikes.to_string(index=False)}\n"
        f"Pooled spike-in slope: {qc.pooled_slope}"
    )


def format_comparison(a: Run, qa: RunQC, b: Run, qb: RunQC) -> str:
    cols = ["n_quantified", "raw_median_z", "corr_to_others"]
    table = pd.concat({a.run_id: qa.metrics[cols], b.run_id: qb.metrics[cols]}, axis=1)
    params = {k: (a.params.get(k), b.params.get(k))
              for k in sorted(set(a.params) | set(b.params))
              if a.params.get(k) != b.params.get(k) and k not in ("outdir", "trace_report_suffix")}
    return (
        f"{a.run_id} -> {b.run_id}\n{table.to_string()}\n\n"
        f"Flagged: {a.run_id}={qa.flagged or 'none'}; {b.run_id}={qb.flagged or 'none'}\n"
        f"Pooled spike-in slope: {qa.pooled_slope} -> {qb.pooled_slope}\n"
        f"Changed parameters (old, new): {params or 'none'}\n"
        f"IsobaricWorkflow command arguments: {command_diff(a.command, b.command)}\n"
        f"Notes: {a.run_id}: {a.note}; {b.run_id}: {b.note}"
    )


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

Approver = Callable[[RerunRequest], tuple[bool, str]]


@dataclass
class LoopResult:
    finish: dict | None
    runs: list[str]
    events: list[dict]
    code_check: dict


class DiagnoseLoop:
    def __init__(self, backend: Backend, approver: Approver, client, model: str | None = None,
                 max_reruns: int = MAX_RERUNS, max_tool_calls: int = MAX_TOOL_CALLS):
        self.backend, self.approver, self.client = backend, approver, client
        self.model = model or default_model()
        self.max_reruns, self.max_tool_calls = max_reruns, max_tool_calls
        self.runs: dict[str, Run] = {}
        self._qc: dict[str, RunQC] = {}
        self.events: list[dict] = []

    def qc(self, run_id: str) -> RunQC:
        if run_id not in self._qc:
            self._qc[run_id] = compute_qc(self.runs[run_id])
        return self._qc[run_id]

    # -- tool implementations ------------------------------------------------

    def _need(self, *run_ids: str) -> str | None:
        missing = [r for r in run_ids if r not in self.runs]
        return f"Unknown run(s) {missing}; existing runs: {list(self.runs)}" if missing else None

    def tool_get_qc(self, run_id: str) -> str:
        return self._need(run_id) or format_qc(self.runs[run_id], self.qc(run_id))

    def tool_get_run_config(self, run_id: str) -> str:
        if err := self._need(run_id):
            return err
        r = self.runs[run_id]
        return (f"Run {run_id} ({r.note})\next.args overrides: {r.ext_args or 'none'}\n\n"
                f"Pipeline parameters:\n{json.dumps(r.params, indent=1)}\n\n"
                f"IsobaricWorkflow command:\n{r.command}")

    def tool_compare_runs(self, run_a: str, run_b: str) -> str:
        if err := self._need(run_a, run_b):
            return err
        a, b = self.runs[run_a], self.runs[run_b]
        return format_comparison(a, self.qc(run_a), b, self.qc(run_b))

    def validate(self, req: RerunRequest) -> str | None:
        if err := self._need(req.base_run):
            return err
        n_done = len(self.runs) - 1
        if n_done >= self.max_reruns:
            return f"Rerun budget used ({self.max_reruns}). Call finish."
        if not req.param_changes and not req.ext_args:
            return "The request changes nothing."
        known = self.runs[req.base_run].params
        bad = [k for k in req.param_changes if k not in known]
        if bad:
            return f"Unknown pipeline parameters {bad}; use names from the parameter JSON."
        bad = [p for p in req.ext_args if p not in KNOWN_PROCESSES]
        if bad:
            return f"Unknown processes {bad}; allowed: {sorted(KNOWN_PROCESSES)}."
        return None

    def tool_request_rerun(self, **kw) -> str:
        for k in ("param_changes", "ext_args"):
            if not isinstance(kw.get(k) or {}, dict):
                return f"Rejected: {k} must be an object."
        req = RerunRequest(kw.get("base_run", ""), kw.get("param_changes") or {},
                           kw.get("ext_args") or {}, kw.get("hypothesis", ""),
                           kw.get("expected_change", ""))
        if err := self.validate(req):
            self.events.append({"event": "rerun_rejected_by_code", "reason": err})
            return f"Rejected: {err}"
        approved, note = self.approver(req)
        self.events.append({"event": "approval", "approved": approved, "note": note})
        if not approved:
            return f"The analyst did not approve this rerun. Note: {note or 'none'}"
        run_id = f"run{len(self.runs)}"
        result = self.backend.rerun(self.runs[req.base_run], req, run_id)
        if isinstance(result, str):
            self.events.append({"event": "rerun_unavailable", "reason": result})
            return result
        self.runs[run_id] = result
        self.events.append({"event": "rerun_done", "run_id": run_id, "note": result.note,
                            "source": result.source})
        return f"Rerun finished as {run_id} ({result.note}). Use get_qc or compare_runs."

    # -- loop ------------------------------------------------------------------

    def call_tool(self, name: str, args: dict) -> str:
        handlers = {
            "get_qc": lambda: self.tool_get_qc(args.get("run_id", "")),
            "get_run_config": lambda: self.tool_get_run_config(args.get("run_id", "")),
            "compare_runs": lambda: self.tool_compare_runs(args.get("run_a", ""), args.get("run_b", "")),
            "request_rerun": lambda: self.tool_request_rerun(**args),
        }
        if name not in handlers:
            return f"Unknown tool {name}"
        return handlers[name]()

    def validate_finish(self, args: dict) -> str | None:
        """The API does not enforce the tool schema, so check it here."""
        spec = next(t["input_schema"] for t in TOOLS if t["name"] == "finish")
        missing = [k for k in spec["required"] if k not in args]
        if missing:
            return f"Missing fields {missing}."
        if args["status"] not in spec["properties"]["status"]["enum"]:
            return f"Invalid status {args['status']!r}."
        if args["final_run"] not in self.runs:
            return f"Unknown final_run {args['final_run']!r}; existing runs: {list(self.runs)}."
        for k in ("remaining_issues", "next_steps"):
            if not isinstance(args[k], list):
                return f"{k} must be a list."
        return None

    def code_check(self, finish: dict | None) -> dict:
        """Compare the model's stated status with the flags computed by code."""
        first = self.qc("run0").flagged
        last_id = finish["final_run"] if finish and finish.get("final_run") in self.runs else list(self.runs)[-1]
        last = self.qc(last_id).flagged
        check = {"flagged_run0": first, "final_run": last_id, "flagged_final_run": last,
                 "status_consistent": None, "conflict": None}
        if finish is None:
            check["conflict"] = "loop ended without finish"
            return check
        status = finish["status"]
        if status == "resolved" and (last or not first or last_id == "run0"):
            check["conflict"] = "status 'resolved' but flags do not support it"
        elif status == "no_action_needed" and first:
            check["conflict"] = "status 'no_action_needed' but run0 has flagged channels"
        check["status_consistent"] = check["conflict"] is None
        return check

    def run(self) -> LoopResult:
        self.runs = {"run0": self.backend.initial_run()}
        self._qc, self.events = {}, []
        messages = [{"role": "user", "content": "A quantms TMT run has finished (run0). "
                     "Investigate its quality and resolve problems if you can."}]
        finish = None
        for n_call in range(self.max_tool_calls):
            response = self.client.messages.create(
                model=self.model, max_tokens=4000, system=SYSTEM, tools=TOOLS,
                messages=messages)
            content = [_block_to_dict(b) for b in response.content]
            # empty text blocks are rejected by the API when sent back
            content = [b for b in content if not (b["type"] == "text" and not b["text"].strip())]
            messages.append({"role": "assistant", "content": content or [{"type": "text", "text": "(no reply)"}]})
            for b in content:
                if b["type"] == "text" and b["text"].strip():
                    self.events.append({"event": "model_text", "text": b["text"]})
            results = []
            for b in content:
                if b["type"] != "tool_use":
                    continue
                self.events.append({"event": "tool_call", "name": b["name"], "input": b["input"]})
                if b["name"] == "finish":
                    if err := self.validate_finish(b["input"]):
                        self.events.append({"event": "finish_rejected_by_code", "reason": err})
                        output = f"Rejected: {err} Call finish again."
                    else:
                        finish = b["input"]
                        output = "Recorded."
                else:
                    output = self.call_tool(b["name"], b["input"])
                self.events.append({"event": "tool_result", "name": b["name"], "output": output})
                results.append({"type": "tool_result", "tool_use_id": b["id"], "content": output})
            if finish is not None:
                break
            if not results:  # the model replied without calling a tool
                self.events.append({"event": "no_tool_call", "stop_reason": response.stop_reason})
                results.append({"type": "text", "text": "Continue by calling a tool; "
                                "call finish to end the investigation."})
            remaining = self.max_tool_calls - n_call - 1
            if remaining <= 1:
                results.append({"type": "text", "text": "Tool budget almost used. Call finish now."})
            messages.append({"role": "user", "content": results})
        return LoopResult(finish, list(self.runs), self.events, self.code_check(finish))


def _block_to_dict(b) -> dict:
    if b.type == "text":
        return {"type": "text", "text": b.text}
    if b.type == "tool_use":
        return {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
    if hasattr(b, "model_dump"):  # e.g. thinking blocks, which must be sent back unchanged
        return b.model_dump(exclude_none=True)
    raise ValueError(f"Unexpected block type {b.type}")


def format_transcript(result: LoopResult, title: str) -> str:
    lines = [f"# {title}", ""]
    for e in result.events:
        if e["event"] == "model_text":
            lines += [f"> {e['text']}", ""]
        elif e["event"] == "tool_call":
            lines += [f"**{e['name']}** `{json.dumps(e['input'])}`", ""]
        elif e["event"] == "tool_result":
            out = e["output"] if len(e["output"]) < 3000 else e["output"][:3000] + "\n[...]"
            lines += ["```", out, "```", ""]
        else:
            lines += [f"- *{e['event']}*: {json.dumps({k: v for k, v in e.items() if k != 'event'})}", ""]
    f = result.finish
    lines += ["## Conclusion (model)", ""]
    if f:
        lines += [f"- Status: {f['status']} (final run: {f['final_run']})",
                  f"- Diagnosis: {f['diagnosis']}", f"- Evidence: {f['evidence']}",
                  f"- Remaining issues: {f['remaining_issues']}", f"- Next steps: {f['next_steps']}"]
    else:
        lines.append("No conclusion (budget exhausted).")
    lines += ["", "## Check by code", "", "```", json.dumps(result.code_check, indent=1), "```"]
    return "\n".join(lines) + "\n"
