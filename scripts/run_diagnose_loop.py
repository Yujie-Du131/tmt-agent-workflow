"""Run the diagnose-rerun agent loop on PXD000001 (replay of recorded quantms runs).

The model starts from the run with the default reporter-ion tolerance
('shift0.002') and may request reruns; replay mode can only return runs that
were actually executed ('shift0.002', 'shift0.01').

Usage (from the repository root):
    uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 \
        examples/diagnose_loop --start shift0.002 --runs 3 --auto-approve

Without --auto-approve, each rerun request is shown and must be approved at
the terminal. --auto-approve stands in for the analyst in benchmark runs and
is recorded in the transcript.
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from tmt_agents.design_check import default_model
from tmt_agents.diagnose_loop import DiagnoseLoop, ReplayBackend, RerunRequest, format_transcript

RECORDED = ["shift0.002", "shift0.01"]


def ask_analyst(req: RerunRequest) -> tuple[bool, str]:
    print("\nRerun requested")
    print(f"  from: {req.base_run}\n  parameters: {req.param_changes}\n  ext.args: {req.ext_args}")
    print(f"  hypothesis: {req.hypothesis}\n  expected: {req.expected_change}")
    answer = input("Approve? [y/N] (optionally followed by a note): ").strip()
    return answer.lower().startswith("y"), answer[1:].strip()


def auto_approve(req: RerunRequest) -> tuple[bool, str]:
    return True, "auto-approved (benchmark run; no analyst)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--start", default="shift0.002", choices=RECORDED)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--auto-approve", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    import anthropic
    client = anthropic.Anthropic()
    approver = auto_approve if args.auto_approve else ask_analyst
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for k in range(1, args.runs + 1):
        backend = ReplayBackend(args.data_dir, args.start, RECORDED)
        result = DiagnoseLoop(backend, approver, client).run()
        stem = f"start_{args.start}_run{k}"
        (args.out_dir / f"{stem}.json").write_text(json.dumps(
            {"model": default_model(), "start": args.start, "auto_approve": args.auto_approve,
             "finish": result.finish, "runs": result.runs, "code_check": result.code_check,
             "events": result.events}, indent=2), encoding="utf-8")
        (args.out_dir / f"{stem}.md").write_text(format_transcript(
            result, f"Diagnose-rerun loop (start {args.start}, run {k}, model `{default_model()}`)"),
            encoding="utf-8")
        n_calls = sum(e["event"] == "tool_call" for e in result.events)
        status = result.finish["status"] if result.finish else None
        print(f"run {k}: status={status}; runs={result.runs}; tool calls={n_calls}; "
              f"code check={result.code_check}")
    print(f"Transcripts written to {args.out_dir}/")


if __name__ == "__main__":
    main()
