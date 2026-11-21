# Assignment 5 — Code Generation and Code Optimization

This implementation bundle accompanies the Assignment 5 report. It is a compact,
runnable educational prototype covering the core required ideas:

- three-address IR, leader discovery, basic-block partitioning and CFG edges;
- backward next-use analysis;
- register/address descriptors and configurable register counts;
- a costed target-code generator;
- redefinition-aware local DAG simplification and peephole cleanup;
- reaching-definitions, live-variable and available-expression data-flow solvers;
- a small test suite and measurement runner.

## Requirements
- Python 3.10 or later
- No third-party Python packages

## Run
```bash
python program.py
python measure.py
python -m unittest -v
```

## Files
- `ir.py` — IR, leaders, blocks, flow graph, next-use
- `codegen.py` — register/address descriptors and target-code generation
- `dag.py` — local DAG simplification and peephole helper
- `dataflow.py` — global data-flow fixed-point solvers
- `opt.py` — constant folding and dead-assignment helper
- `program.py` — integrated demonstration
- `measure.py` — register-count measurements
- `test_assignment5.py` — unit tests

## Important scope note
This is a teaching prototype, not a production compiler. The code generator uses a
small illustrative target instruction model. For a formal submission, run the
programs in your own environment, inspect the generated outputs, and capture
genuine screenshots from your terminal/IDE. Do not represent generated report
figures as screenshots from a live IDE.
