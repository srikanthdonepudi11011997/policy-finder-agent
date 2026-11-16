"""Command line: python -m policy_agent.cli <folder> list | versions <name> | ask <question>"""

from __future__ import annotations

import argparse

from .agent import PolicyAgent


def main() -> None:
    p = argparse.ArgumentParser(prog="policy-agent")
    p.add_argument("folder", help="folder containing policy documents")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="show the latest approved version of every policy")
    v = sub.add_parser("versions", help="show every version of one policy")
    v.add_argument("name")
    a = sub.add_parser("ask", help="ask a question about the current policies")
    a.add_argument("question", nargs="+")
    args = p.parse_args()

    agent = PolicyAgent(args.folder)
    if args.cmd == "list":
        for d in agent.latest_policies():
            print(f"{d.policy_name:<28} v{d.version:<6} {d.effective_date}  {d.path}")
    elif args.cmd == "versions":
        for d in agent.versions(args.name):
            print(f"v{d.version:<6} {d.effective_date}  {d.status:<9} {d.path}")
    else:
        ans = agent.ask(" ".join(args.question))
        print(ans.text)
        for s in ans.sources:
            print(f"\nSource: {s}")


if __name__ == "__main__":
    main()
