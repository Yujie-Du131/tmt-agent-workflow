"""Run the diagnose-rerun agent loop on PXD000001.

Two backends:

- replay (default): reruns are answered from the recorded quantms runs in
  data_dir ('shift0.002', 'shift0.01'); anything else is refused.
- live (--live WORKDIR): every run, including the first, is a real
  `nextflow run bigbio/quantms -r 1.10.0 -profile test_tmt,docker -resume`
  launched from WORKDIR. Needs Nextflow and Docker. Launch from the folder
  of an earlier quantms run (the one with `.nextflow/` and `work/`) to reuse
  its cached tasks.

--start picks the first run: 'shift0.002' (default reporter tolerance) or
'shift0.01' (with -extraction:reporter_mass_shift 0.01 passed via ext.args).

Usage (from the repository root):
    # replay
    uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 \
        examples/diagnose_loop --start shift0.002 --runs 3 --auto-approve
    # live, approving each rerun at the terminal; pass the config and fixed
    # parameters of the earlier runs so that their cache is reused
    uv run python scripts/run_diagnose_loop.py data/quantms_pxd000001 \
        examples/diagnose_loop_live --start shift0.002 --live ~/quantms_test \
        --nf-config ~/quantms_test/small.config \
        --nf-param root_folder=/home/ubuntu/pxd000001 --nf-param local_input_type=raw

Without --auto-approve, each rerun request is shown and must be approved at
the terminal. --auto-approve stands in for the analyst in benchmark runs and
is recorded in the transcript.
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from tmt_agents.design_check import default_model
from tmt_agents.diagnose_loop import (
    DiagnoseLoop,
    NextflowBackend,
    ReplayBackend,
    RerunRequest,
    format_transcript,
)

# Recorded quantms runs and the ext.args each was made with.
RECORDED = {
    "shift0.002": {},
    "shift0.01": {"ISOBARIC_WORKFLOW": "-extraction:reporter_mass_shift 0.01"},
}


def ask_analyst(req: RerunRequest) -> tuple[bool, str]:
    print("\nRerun requested")
    print(f"  from: {req.base_run}\n  parameters: {req.param_changes}\n  ext.args: {req.ext_args}")
    print(f"  hypothesis: {req.hypothesis}\n  expected: {req.expected_change}")
    answer = input("Approve? [y/N] (optionally followed by a note): ").strip()
    first, _, note = answer.partition(" ")
    return first.lower().startswith("y"), note.strip()


def auto_approve(req: RerunRequest) -> tuple[bool, str]:
    return True, "auto-approved (benchmark run; no analyst)"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--start", default="shift0.002", choices=list(RECORDED))
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--auto-approve", action="store_true")
    parser.add_argument("--live", type=Path, metavar="WORKDIR",
                        help="run quantms for real, launched from WORKDIR")
    parser.add_argument("--nf-config", type=Path, action="append", default=[],
                        help="extra Nextflow config used by earlier runs (live mode; repeatable)")
    parser.add_argument("--nf-param", action="append", default=[], metavar="KEY=VALUE",
                        help="pipeline parameter passed on every run (live mode; repeatable)")
    args = parser.parse_args()

    load_dotenv()
    import anthropic
    client = anthropic.Anthropic()
    approver = auto_approve if args.auto_approve else ask_analyst
    args.out_dir.mkdir(parents=True, exist_ok=True)
    mode = "live" if args.live else "replay"

    for k in range(1, args.runs + 1):
        if args.live:
            print(f"Starting the first quantms run in {args.live} (can take about 25 min "
                  "unless cached)...")
            fixed = dict(p.split("=", 1) for p in args.nf_param)
            backend = NextflowBackend(args.live, initial_ext_args=RECORDED[args.start],
                                      user_configs=args.nf_config, fixed_params=fixed)
        else:
            backend = ReplayBackend(args.data_dir, args.start, RECORDED)
        result = DiagnoseLoop(backend, approver, client).run()
        stem = f"{'live_' if args.live else ''}start_{args.start}_run{k}"
        (args.out_dir / f"{stem}.json").write_text(json.dumps(
            {"model": default_model(), "backend": mode, "start": args.start,
             "auto_approve": args.auto_approve, "finish": result.finish, "runs": result.runs,
             "code_check": result.code_check, "events": result.events}, indent=2), encoding="utf-8")
        (args.out_dir / f"{stem}.md").write_text(format_transcript(
            result, f"Diagnose-rerun loop ({mode}, start {args.start}, run {k}, "
                    f"model `{default_model()}`)"), encoding="utf-8")
        n_calls = sum(e["event"] == "tool_call" for e in result.events)
        status = result.finish["status"] if result.finish else None
        print(f"run {k}: status={status}; runs={result.runs}; tool calls={n_calls}; "
              f"code check={result.code_check}")
    print(f"Transcripts written to {args.out_dir}/")


if __name__ == "__main__":
    main()
