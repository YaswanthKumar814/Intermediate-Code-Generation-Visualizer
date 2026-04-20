# Intermediate Code Generation Visualizer

An educational compiler project for a small C-like language. The project demonstrates the full pipeline from source code to intermediate representation, optimization, and AST visualization.

## Overview

The compiler currently supports:

- lexical analysis using PLY
- parsing and AST generation using PLY yacc
- semantic checks for undeclared variables and redeclaration
- three-address code (TAC) generation
- basic optimization
- AST visualization using Graphviz
- a simple Flask-based web UI for interactive use

This project is designed for compiler design coursework, demonstrations, and viva presentations.

## Compiler Pipeline

The project processes source code in the following order:

1. Source code input
2. Lexical analysis
3. Parsing
4. Abstract syntax tree construction
5. Semantic validation
6. Three-address code generation
7. Optimization
8. AST visualization

## Supported Language Features

### Declarations and statements

- variable declaration
- assignment
- `print(...)`
- `if`
- `if-else`
- `while`
- `for`

### Expressions

- arithmetic: `+`, `-`, `*`, `/`
- unary minus
- relational: `>`, `<`, `>=`, `<=`, `==`, `!=`
- logical: `&&`, `||`
- grouped expressions with parentheses

### Comments

- single-line comments: `// comment`
- multi-line comments: `/* comment */`

## Example Program

```c
int a = 5;
int b = 10;
int c;

if (a < b && b != 0) {
    c = a + b * 2;
    print(c);
}
```

## Project Structure

```text
compiler_visualizer/
├── app.py
├── ast_nodes.py
├── lexer.py
├── main.py
├── optimizer.py
├── parser.py
├── symbol_table.py
├── tac_generator.py
├── visualizer.py
├── requirements.txt
├── outputs/
├── static/
├── templates/
└── tests/
```

## File Descriptions

### `lexer.py`

Handles lexical analysis using PLY.

- tokenizes identifiers, numbers, keywords, operators, separators
- ignores whitespace and comments
- reports clear lexical errors with line and column information

### `parser.py`

Handles syntax analysis and AST construction.

- defines grammar rules
- enforces operator precedence
- supports control-flow statements
- performs semantic validation after parsing
- replaces missing optional `for` parts with `Empty` AST nodes

### `ast_nodes.py`

Defines the reusable AST node structure used across the compiler pipeline.

### `symbol_table.py`

Defines symbol table and semantic error helpers used during validation.

### `tac_generator.py`

Converts the AST into three-address code.

- uses temporary variables like `t1`, `t2`
- uses labels like `L1`, `L2`
- supports TAC generation for control flow

### `optimizer.py`

Applies safe optimizations to TAC.

- constant folding
- common subexpression elimination
- dead code elimination for straight-line TAC
- basic-block-aware safety when control flow exists

### `visualizer.py`

Builds and renders the AST using Graphviz.

- creates `.png` output
- handles missing AST nodes safely using `Empty`

### `main.py`

Command-line entry point for the compiler pipeline.

- prints tokens
- prints AST
- prints TAC before and after optimization
- generates AST visualization in `outputs/`

### `app.py`

Optional Flask web UI.

- lets users enter code in a browser
- runs the compiler pipeline
- shows TAC and AST image output

## Installation

## Prerequisites

- Python 3.10 or later recommended
- Graphviz system installation for AST image rendering

## Install Python dependencies

```bash
pip install -r requirements.txt
```

If you want to use the web UI and `Flask` is not already installed:

```bash
pip install flask
```

## Install Graphviz

You need both:

- the Python `graphviz` package
- the Graphviz system binaries

On Windows:

1. Download and install Graphviz from the official site.
2. Add the Graphviz `bin` directory to `PATH`.
3. Verify installation:

```bash
dot -V
```

## Running the Project

### Command-line mode

Run the sample program bundled in `main.py`:

```bash
python main.py
```

Run a source file:

```bash
python main.py path/to/program.src
```

### Web UI mode

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Example Output Stages

The command-line pipeline prints:

- source code
- tokens
- AST
- TAC before optimization
- TAC after optimization
- optimization summary
- visualization status

## Test Suite

The project includes a lightweight test suite under `tests/`.

### Run tests

```bash
python tests/run_tests.py
```

The tests cover:

- valid programs
- invalid programs
- edge cases
- `if` statement cases
- division by zero
- nested expressions

## Error Handling

The compiler reports readable messages for:

- lexical errors
- syntax errors
- undeclared variables
- redeclaration of variables
- division by zero during optimization
- missing Graphviz installation

The parser and visualizer also include extra safety for:

- empty input
- `for (;;)`
- malformed or missing AST nodes

## Current Design Notes

This is an educational compiler subset, not a full production compiler.

Important design choices:

- conditions are supported in `if`, `while`, and `for`
- missing `for` components are represented with `Empty` AST nodes
- control-flow optimization is intentionally conservative for correctness
- the optimizer focuses mainly on arithmetic TAC

## Sample Supported Programs

### While loop

```c
int a = 3;
while (a) {
    print(a);
    a = a - 1;
}
```

### For loop

```c
for (int i = 3; i > 0; i = i - 1) {
    print(i);
}
```

### If-else

```c
int a = 5;
if (a > 0) {
    print(a);
} else {
    print(0);
}
```

## Limitations

- optimization is intentionally conservative in the presence of control flow
- semantic analysis uses a simple symbol-table model
- the language is a small teaching subset, not full C

## Use Cases

- compiler design coursework
- lab demonstrations
- viva presentations
- AST and TAC visualization demos

## Authors / Submission Note

This repository is suitable for academic project submission after:

- verifying Graphviz installation
- running the test suite
- checking that CLI and optional UI both work correctly on the target machine

