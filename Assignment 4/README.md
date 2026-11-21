# Assignment 4 – Part II: Compiler Engineering Implementation

Python 3 standard-library implementation organized by the six assignment tasks. No third-party packages are required.

## Run

From this directory:

```bash
python mini.py                 # integrated demonstration
python symtab.py               # Task 1
python expr.py                 # Task 2
python bool.py                 # Task 3
python case.py                 # Task 4
python calls.py                # Task 5
python -m unittest discover -s tests -v
```

## Files

- `symtab.py` – primitive, pointer, array and record types; nested scopes; duplicate/invalid-array checks; alignment and offset trace.
- `ir.py` – quadruple emitter, triples, indirect-triple ordering, backpatching and unresolved-target checker.
- `expr.py` – arithmetic expression translation, unary minus, widening conversions, array loads/bounds checks, value numbering and temporary trace.
- `bool.py` – short-circuit AND/OR list composition and backpatching consistency demonstration.
- `case.py` – sequential, binary-search and jump-table switch dispatch, default validation and comparison counters.
- `calls.py` – argument queue, call/return sequence and activation-record layout.
- `mini.py` – integrated demonstration runner and small deterministic test-vector summary.

## Important scope notes

This is an executable teaching prototype, not a production compiler. The expression front end accepts Python-style arithmetic expressions and supports a focused subset of AST forms. Boolean control-flow and procedure-call examples expose the translation machinery rather than providing a complete source-language parser. `mini.py` labels the five integration outcomes as reference test vectors; it does not claim to execute arbitrary recursive/array programs. Extend the parser and interpreter if the evaluator expects a complete language implementation.

For actual submission evidence, run the scripts in your own Python environment and capture genuine terminal screenshots. The console-style images in the accompanying report are illustrative, not live screenshots.
