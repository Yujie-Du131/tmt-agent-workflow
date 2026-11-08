"""Tests for the diagnose-rerun loop, using a scripted model (no API calls).

The replay backend is run on the recorded PXD000001 quantms outputs.
"""

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from tmt_agents.diagnose_loop import (
    DiagnoseLoop,
    NextflowBackend,
    ReplayBackend,
    command_diff,
    compute_qc,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "quantms_pxd000001"
FIX = {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"}
RECORDED = {"shift0.002": {}, "shift0.01": FIX}


class ScriptedClient:
    """Returns one scripted tool call per request and records what it was sent."""

    def __init__(self, calls):
        self.calls = list(calls)
        self.sent = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        assert "tool_choice" not in kw  # forced tool use is not supported by all models
        self.sent.append(kw["messages"][-1])
        name, args = self.calls.pop(0)
        if name == "text":  # a reply without a tool call
            return SimpleNamespace(content=[SimpleNamespace(type="text", text=args)],
                                   stop_reason="end_turn")
        block = SimpleNamespace(type="tool_use", id=f"t{len(self.sent)}", name=name, input=args)
        return SimpleNamespace(content=[block], stop_reason="tool_use")

    def last_result(self, index=-1):
        return self.sent[index]["content"][0]["content"]


def rerun(base, params=None, ext=None):
    return ("request_rerun", {"base_run": base, "param_changes": params or {}, "ext_args": ext or {},
                              "hypothesis": "h", "expected_change": "e"})


def finish(status, final_run):
    return ("finish", {"status": status, "final_run": final_run, "diagnosis": "d", "evidence": "e",
                       "remaining_issues": [], "next_steps": []})


class Approver:
    def __init__(self, answer=True):
        self.answer, self.requests = answer, []

    def __call__(self, req):
        self.requests.append(req)
        return self.answer, ""


def make_loop(calls, approver=None, start="shift0.002", **kw):
    client = ScriptedClient(calls)
    backend = ReplayBackend(DATA, start, RECORDED)
    loop = DiagnoseLoop(backend, approver or Approver(), client, model="test", **kw)
    return loop, client


def test_flags_on_recorded_runs():
    r0 = ReplayBackend(DATA, "shift0.002", RECORDED).initial_run()
    r1 = ReplayBackend(DATA, "shift0.01", RECORDED).initial_run()
    assert compute_qc(r0).flagged == ["ch2", "ch4"]
    assert compute_qc(r1).flagged == []


def test_manual_path_param_has_no_effect_then_ext_args_fixes():
    """Reproduces the manual investigation: the pipeline parameter does not reach
    IsobaricWorkflow; passing the option through ext.args recovers the channels."""
    loop, client = make_loop([
        ("get_qc", {"run_id": "run0"}),
        rerun("run0", params={"reporter_mass_shift": 0.01}),
        ("compare_runs", {"run_a": "run0", "run_b": "run1"}),
        rerun("run1", ext=FIX),
        ("compare_runs", {"run_a": "run0", "run_b": "run2"}),
        finish("resolved", "run2"),
    ])
    result = loop.run()
    assert "Flagged by code" in client.last_result(1) and "['ch2', 'ch4']" in client.last_result(1)
    no_effect = client.last_result(3)
    assert "reporter_mass_shift': (0.002, 0.01)" in no_effect
    assert "'added': []" in no_effect and "ISOBARIC_WORKFLOW as cached" in no_effect
    assert "shift0" not in "".join(str(m["content"]) for m in client.sent)  # no hint from file names
    fixed = client.last_result(5)
    assert "run2=none" in fixed and "-extraction:reporter_mass_shift" in fixed
    assert result.runs == ["run0", "run1", "run2"]
    assert result.code_check["status_consistent"] is True
    assert loop.runs["run2"].ext_args == FIX


def test_unrecorded_change_is_unavailable():
    loop, client = make_loop([rerun("run0", params={"isotope_correction": True}),
                              rerun("run0", ext={"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.02"}),
                              finish("unresolved", "run0")])
    result = loop.run()
    assert client.last_result(1).startswith("Not available in replay mode")
    assert client.last_result(2).startswith("Not available in replay mode")
    assert result.runs == ["run0"]
    assert result.code_check["status_consistent"] is True


def test_invalid_requests_rejected_before_approval():
    approver = Approver()
    loop, client = make_loop([rerun("run0", params={"no_such_param": 1}),
                              rerun("run0", ext={"SEARCHENGINECOMET": "-x 1"}),
                              rerun("run0"),
                              rerun("run9", ext=FIX),
                              finish("unresolved", "run0")], approver)
    loop.run()
    assert approver.requests == []
    assert "Unknown pipeline parameters" in client.last_result(1)
    assert "Unknown processes" in client.last_result(2)
    assert "changes nothing" in client.last_result(3)
    assert "Unknown run" in client.last_result(4)


def test_refused_approval_creates_no_run():
    loop, client = make_loop([rerun("run0", ext=FIX), finish("unresolved", "run0")], Approver(False))
    result = loop.run()
    assert "did not approve" in client.last_result(1)
    assert result.runs == ["run0"]


def test_rerun_budget():
    loop, client = make_loop([rerun("run0", ext=FIX), rerun("run1", params={"reporter_mass_shift": 0.01}),
                              finish("resolved", "run1")], max_reruns=1)
    result = loop.run()
    assert "budget used" in client.last_result(2)
    assert result.runs == ["run0", "run1"]


@pytest.mark.parametrize("status,final,conflict", [
    ("resolved", "run0", True),         # nothing was rerun
    ("no_action_needed", "run0", True), # run0 has flagged channels
    ("unresolved", "run0", False),
])
def test_status_checked_by_code(status, final, conflict):
    loop, _ = make_loop([finish(status, final)])
    result = loop.run()
    assert (result.code_check["conflict"] is not None) == conflict


def test_tool_budget_without_finish():
    loop, client = make_loop([("get_qc", {"run_id": "run0"})] * 3, max_tool_calls=3)
    result = loop.run()
    assert result.finish is None
    assert result.code_check["conflict"] == "loop ended without finish"
    assert client.sent[-1]["content"][-1]["text"].startswith("Tool budget almost used")


def test_command_diff_detects_added_option():
    a = (DATA / "isobaric_command_shift0.002.sh").read_text()
    b = (DATA / "isobaric_command_shift0.01.sh").read_text()
    assert command_diff(a, b) == {"removed": [], "added": ["-extraction:reporter_mass_shift", "0.01"]}
    assert command_diff(a, a) == {"removed": [], "added": []}


def test_nextflow_backend_builds_config_and_command(tmp_path):
    nf = NextflowBackend(tmp_path, runner=lambda *a: 0)
    cfg = nf.config_text(FIX)
    assert "withName: '.*:ISOBARIC_WORKFLOW' { ext.args = \"-extraction:reporter_mass_shift 0.01\" }" in cfg
    cmd = nf.command({"isotope_correction": True}, tmp_path / "run1.config", "results_run1", "agent_x_run1")
    assert cmd[:6] == ["nextflow", "run", "bigbio/quantms", "-r", "1.10.0", "-profile"]
    assert "-resume" in cmd and cmd[cmd.index("-name") + 1] == "agent_x_run1"
    assert cmd[-2:] == ["--isotope_correction", "true"]


class FakeNextflow:
    """Stands in for `nextflow run`: writes outputs from the recorded runs.

    The output depends only on the ext.args in the config (as for quantms
    1.10.0 with the parameters used here); the IsobaricWorkflow command is the
    recorded one plus the ext.args.
    """

    def __init__(self, root, fail=False):
        self.root, self.fail, self.commands, self.task_dirs = root, fail, [], {}

    def __call__(self, cmd, cwd, log):
        self.commands.append(cmd)
        log.write_text("nextflow log\n")
        if self.fail:
            return 1
        name = cmd[cmd.index("-name") + 1]
        outdir = Path(cwd) / cmd[cmd.index("--outdir") + 1]
        configs = [cmd[i + 1] for i, t in enumerate(cmd) if t == "-c"]
        fixed = any("reporter_mass_shift 0.01" in Path(c).read_text() for c in configs)
        tag = "shift0.01" if fixed else "shift0.002"
        (outdir / "quant_tables").mkdir(parents=True)
        (outdir / "pipeline_info").mkdir()
        df = pd.read_csv(DATA / f"msstats_in_{tag}.csv.gz")
        df.to_csv(outdir / "quant_tables" / "PXD000001_msstats_in.csv", index=False)
        params = json.loads((DATA / "params_shift0.002.json").read_text())
        i = cmd.index("--outdir") + 2
        while i < len(cmd):
            params[cmd[i][2:]] = cmd[i + 1]
            i += 2
        (outdir / "pipeline_info" / "params_2026.json").write_text(json.dumps(params))
        task = Path(cwd) / "work" / ("fixed" if fixed else "default")
        task.mkdir(parents=True, exist_ok=True)
        (task / ".command.sh").write_text((DATA / f"isobaric_command_{tag}.sh").read_text())
        self.task_dirs[name] = task
        return 0

    def log(self, name, cwd):
        return f"BIGBIO_QUANTMS:QUANTMS:TMT:ISOBARIC_WORKFLOW (PXD000001)\t{self.task_dirs[name]}\n"


def test_live_backend_with_fake_nextflow(tmp_path):
    fake = FakeNextflow(tmp_path)
    backend = NextflowBackend(tmp_path, runner=fake, log_reader=fake.log)
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "tmt6plex_default_correction.matrix").write_text("x")
    client = ScriptedClient([
        ("get_run_config", {"run_id": "run0"}),
        rerun("run0", params={"reporter_mass_shift": 0.01}),
        rerun("run0", ext=FIX),
        rerun("run2", params={"min_precursor_purity": 0.5}),
        ("compare_runs", {"run_a": "run0", "run_b": "run2"}),
        finish("resolved", "run3"),
    ])
    loop = DiagnoseLoop(backend, Approver(), client, model="test")
    result = loop.run()
    assert "assets/tmt6plex_default_correction.matrix" in client.last_result(1)
    assert "command unchanged" in loop.runs["run1"].note
    assert compute_qc(loop.runs["run2"]).flagged == []
    run3_cmd = fake.commands[3]
    assert run3_cmd[-2:] == ["--min_precursor_purity", "0.5"]  # overrides accumulate from run2
    agent_cfg = [run3_cmd[i + 1] for i, t in enumerate(run3_cmd) if t == "-c"][-1]
    assert "reporter_mass_shift 0.01" in Path(agent_cfg).read_text()
    assert loop.runs["run3"].overrides == {"min_precursor_purity": 0.5}
    assert result.code_check["status_consistent"] is True
    assert "run2=none" in client.last_result(5)


def test_live_backend_failure_is_reported(tmp_path):
    ok, failing = FakeNextflow(tmp_path), FakeNextflow(tmp_path, fail=True)

    def runner(cmd, cwd, log):  # run0 succeeds, every rerun fails
        name = cmd[cmd.index("-name") + 1]
        return ok(cmd, cwd, log) if name.endswith("_run0") else failing(cmd, cwd, log)

    backend = NextflowBackend(tmp_path, runner=runner, log_reader=ok.log)
    client = ScriptedClient([rerun("run0", ext=FIX), finish("unresolved", "run0")])
    result = DiagnoseLoop(backend, Approver(), client, model="test").run()
    assert result.runs == ["run0"]
    assert any(e["event"] == "rerun_unavailable" and "Nextflow failed (exit 1)" in e["reason"]
               for e in result.events)

def test_reply_without_tool_call_is_nudged():
    loop, client = make_loop([("text", "Let me think."), finish("unresolved", "run0")])
    result = loop.run()
    assert client.sent[1]["content"][0]["text"].startswith("Continue by calling a tool")
    assert any(e["event"] == "no_tool_call" for e in result.events)
    assert result.finish is not None


def test_incomplete_finish_is_rejected():
    incomplete = ("finish", {"status": "unresolved", "final_run": "run0", "diagnosis": "d",
                             "evidence": "e", "remaining_issues": []})
    loop, client = make_loop([incomplete, ("finish", {**incomplete[1], "final_run": "run7", "next_steps": []}),
                              finish("unresolved", "run0")])
    result = loop.run()
    assert "Missing fields ['next_steps']" in client.last_result(1)
    assert "Unknown final_run" in client.last_result(2)
    assert result.finish["next_steps"] == []
    assert sum(e["event"] == "finish_rejected_by_code" for e in result.events) == 2


def test_fixed_run_shows_its_ext_args_and_can_be_reverted():
    """Starting from the fixed run (control): its ext.args are reported, and
    reverting the option (explicit default or removal) returns the default run."""
    loop, client = make_loop([
        ("get_run_config", {"run_id": "run0"}),
        rerun("run0", ext={"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.002"}),
        rerun("run0", ext={"ISOBARIC_WORKFLOW": ""}),
        ("compare_runs", {"run_a": "run0", "run_b": "run1"}),
        finish("unresolved", "run0"),
    ], start="shift0.01")
    result = loop.run()
    assert "ext.args overrides: {'ISOBARIC_WORKFLOW': '-extraction:reporter_mass_shift 0.01'}" in client.last_result(1)
    assert result.runs == ["run0", "run1", "run2"]
    assert compute_qc(loop.runs["run1"]).flagged == ["ch2", "ch4"]
    assert compute_qc(loop.runs["run2"]).flagged == ["ch2", "ch4"]
    assert loop.runs["run2"].ext_args == {}
    assert "run1=['ch2', 'ch4']" in client.last_result(4) and "corr_to_others" in client.last_result(4)
    # the explicit default argument appears in the command, as in a live run
    assert command_diff(loop.runs["run0"].command, loop.runs["run1"].command) == {
        "removed": ["0.01"], "added": ["0.002"]}
    assert command_diff(loop.runs["run0"].command, loop.runs["run2"].command) == {
        "removed": ["-extraction:reporter_mass_shift", "0.01"], "added": []}


def test_param_change_from_fixed_run_keeps_fix():
    loop, _ = make_loop([rerun("run0", params={"reporter_mass_shift": 0.002}), finish("unresolved", "run0")],
                        start="shift0.01")
    loop.run()
    assert compute_qc(loop.runs["run1"]).flagged == []
    assert "cached" in loop.runs["run1"].note


FAKE_NEXTFLOW = r'''#!/usr/bin/env python3
"""Fake `nextflow` executable for tests: `run` writes outputs, `log` lists the task."""
import gzip, json, shutil, sys
from pathlib import Path
DATA = Path(sys.argv[0]).parent / "data"
args = sys.argv[1:]
state = Path(".fake_nf.json")
tasks = json.loads(state.read_text()) if state.exists() else {}
if args[0] == "log":
    print(f"BIGBIO_QUANTMS:QUANTMS:TMT:ISOBARIC_WORKFLOW (PXD000001)\t{tasks[args[1]]}")
    sys.exit(0)
name, out = args[args.index("-name") + 1], Path(args[args.index("--outdir") + 1])
configs = [args[i + 1] for i, t in enumerate(args) if t == "-c"]
tag = "shift0.01" if any("0.01" in Path(c).read_text() for c in configs) else "shift0.002"
(out / "quant_tables").mkdir(parents=True)
(out / "pipeline_info").mkdir()
with gzip.open(DATA / f"msstats_in_{tag}.csv.gz") as src, open(out / "quant_tables" / "x_msstats_in.csv", "wb") as dst:
    shutil.copyfileobj(src, dst)
shutil.copy(DATA / f"params_{tag}.json", out / "pipeline_info" / "params_1.json")
task = Path("work") / tag
task.mkdir(parents=True, exist_ok=True)
shutil.copy(DATA / f"isobaric_command_{tag}.sh", task / ".command.sh")
tasks[name] = str(task.resolve())
state.write_text(json.dumps(tasks))
print("fake nextflow done")
'''


def test_live_backend_with_fake_executable(tmp_path, monkeypatch):
    """Exercises the real subprocess path (run, log file, `nextflow log` parsing)."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    exe = bindir / "nextflow"
    exe.write_text(FAKE_NEXTFLOW)
    exe.chmod(0o755)
    (bindir / "data").symlink_to(DATA)
    assets = tmp_path / "nxf_assets" / "bigbio" / "quantms" / "assets"
    assets.mkdir(parents=True)
    (assets / "tmt6plex_default_correction.matrix").write_text("x")
    monkeypatch.setenv("PATH", f"{bindir}:{os.environ['PATH']}")
    monkeypatch.setenv("NXF_ASSETS", str(tmp_path / "nxf_assets"))
    work = tmp_path / "launch"
    backend = NextflowBackend(work)
    client = ScriptedClient([rerun("run0", ext=FIX), finish("resolved", "run1")])
    result = DiagnoseLoop(backend, Approver(), client, model="test").run()
    assert result.runs == ["run0", "run1"]
    assert result.code_check["flagged_run0"] == ["ch2", "ch4"]
    assert result.code_check["status_consistent"] is True
    assert (work / "assets" / "tmt6plex_default_correction.matrix").exists()
    assert "fake nextflow done" in (work / f"agent_{backend.stamp}_run1.log").read_text()


def test_live_backend_user_config_and_fixed_params(tmp_path):
    user_cfg = tmp_path / "small.config"
    user_cfg.write_text("process { resourceLimits = [cpus: 2, memory: 7.GB] }")
    nf = NextflowBackend(tmp_path, user_configs=[user_cfg],
                         fixed_params={"root_folder": "/data/pxd", "local_input_type": "raw"})
    cmd = nf.command({"min_precursor_purity": 0.5}, tmp_path / "agent.config", "out", "agent_x_run1")
    configs = [cmd[i + 1] for i, t in enumerate(cmd) if t == "-c"]
    assert configs == [str(user_cfg.resolve()), str(tmp_path / "agent.config")]  # user config first
    assert cmd[cmd.index("--root_folder") + 1] == "/data/pxd"
    assert cmd[-2:] == ["--min_precursor_purity", "0.5"]
    assert "resourceLimits" not in nf.config_text(FIX)


def test_assets_found_in_nested_layout(tmp_path, monkeypatch):
    nested = tmp_path / "nxf" / ".repos" / "bigbio" / "quantms" / "clones" / "6a721f0" / "assets"
    nested.mkdir(parents=True)
    (nested / "tmt6plex_default_correction.matrix").write_text("x")
    monkeypatch.setenv("NXF_ASSETS", str(tmp_path / "nxf"))
    nf = NextflowBackend(tmp_path / "launch", runner=lambda *a: 0)
    nf._stage_assets()
    assert nf.available_files() == ["assets/tmt6plex_default_correction.matrix"]
