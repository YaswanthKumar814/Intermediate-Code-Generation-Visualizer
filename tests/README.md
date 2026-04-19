# Test Suite

This folder contains sample programs and a lightweight runner for validating the compiler pipeline.

## Coverage

- `valid/` contains programs that should compile successfully.
- `invalid/` contains programs that should fail with clear semantic or syntax errors.
- `edge/` contains corner cases such as division by zero and complex nesting.

## Run

From the `compiler_visualizer` folder:

```powershell
python tests\run_tests.py
```

If Python is exposed as `py` on your machine, use:

```powershell
py tests\run_tests.py
```
