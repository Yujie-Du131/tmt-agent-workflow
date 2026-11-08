"""Tests for the diagnose-rerun loop, using a scripted model (no API calls).

The replay backend is run on the recorded PXD000001 quantms outputs.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from tmt_agents.diagnose_loop import (
    DiagnoseLoop,
    NextflowBackend,
    ReplayBackend,
    Run,
    command_diff,
    compute_qc,
)

DATA = Path(__file__).resolve().parents[1] / "data" / "quantms_pxd000001"
RECORDED = ["shift0.002", "shift0.01"]
FIX = {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"}


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


def make_loop(calls, approver=None, **kw):
    client = ScriptedClient(calls)
    backend = ReplayBackend(DATA, "shift0.002", RECORDED)
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
    initial = Run("run0", tmp_path / "x.csv", {}, "")
    nf = NextflowBackend(tmp_path, initial)
    cfg = nf.config_text(FIX)
    assert "withName: '.*:ISOBARIC_WORKFLOW' { ext.args = \"-extraction:reporter_mass_shift 0.01\" }" in cfg
    cmd = nf.command({"isotope_correction": True}, tmp_path / "run1.config", "results_run1")
    assert cmd[:6] == ["nextflow", "run", "bigbio/quantms", "-r", "1.10.0", "-profile"]
    assert "-resume" in cmd and cmd[-2:] == ["--isotope_correction", "true"]


def test_reply_without_tool_call_is_nudged():
    loop, client = make_loop([("text", "Let me think."), finish("unresolved", "run0")])
    result = loop.run()
    assert client.sent[1]["content"][0]["text"].startswith("Continue by calling a tool")
    assert any(e["event"] == "no_tool_call" for e in result.events)
    assert result.finish is not None
