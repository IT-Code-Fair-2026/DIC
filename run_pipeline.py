"""
Run every notebook in notebooks/ in order, so data/processed/ is rebuilt from
data/raw/ and data/external/ exactly the same way every time.

    python run_pipeline.py              # run all notebooks (00a -> 11)
    python run_pipeline.py --from 07    # start at a given notebook number
    python run_pipeline.py --only 08    # run a single notebook

Each notebook is executed in place (its saved outputs are refreshed), with the
repo root as the working directory. The run stops at the first notebook that
raises an error.
"""
import argparse
import sys
import time
from pathlib import Path

import nbformat
from nbconvert.preprocessors import CellExecutionError, ExecutePreprocessor

ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = ROOT / "notebooks"
TIMEOUT_S = 1800  # per cell; notebook 03 reads the ~400 MB ACMA register


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--from", dest="start", help="first notebook number to run, e.g. 07")
    group.add_argument("--only", help="run just this notebook number, e.g. 08")
    args = parser.parse_args()

    # Notebook file names start with their run order (00a, 00b, 01 ... 11), so a sort is the order.
    notebooks = sorted(NOTEBOOK_DIR.glob("*.ipynb"))
    if args.only:
        notebooks = [nb for nb in notebooks if nb.name.startswith(args.only)]
    elif args.start:
        notebooks = [nb for nb in notebooks if nb.name >= args.start]
    if not notebooks:
        print("no notebooks matched", file=sys.stderr)
        return 1

    for path in notebooks:
        print(f"running {path.name} ...", end=" ", flush=True)
        started = time.time()
        nb = nbformat.read(path, as_version=4)
        executor = ExecutePreprocessor(timeout=TIMEOUT_S, kernel_name="python3")
        try:
            executor.preprocess(nb, {"metadata": {"path": str(ROOT)}})
        except CellExecutionError as err:
            nbformat.write(nb, path)  # keep the traceback in the notebook for inspection
            print(f"FAILED\n\n{err}", file=sys.stderr)
            return 1
        nbformat.write(nb, path)
        print(f"ok ({time.time() - started:.0f}s)")

    print(f"\ndone: {len(notebooks)} notebook(s); outputs are in data/processed/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
