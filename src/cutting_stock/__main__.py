from __future__ import annotations

import argparse
import json

from .experiment import run_demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Run column generation on a cutting-stock instance.")
    parser.add_argument("--tolerance", type=float, default=1e-9)
    parser.add_argument("--max-iterations", type=int, default=100)
    args = parser.parse_args()
    print(json.dumps(run_demo(args.tolerance, args.max_iterations), indent=2))


if __name__ == "__main__":
    main()
