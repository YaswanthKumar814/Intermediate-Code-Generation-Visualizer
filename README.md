# Intermediate Code Generation Visualizer

This project is a modular educational compiler demo for a small C-like language. It is intended to show the major compiler stages clearly: lexical analysis, syntax analysis, abstract syntax tree construction, three-address code generation, optimization, and visualization.

## Module Overview

- `main.py` coordinates the pipeline and command-line entry point.
- `lexer.py` defines tokens and exposes the lexical analysis interface.
- `parser.py` defines grammar rules and produces AST nodes.
- `ast_nodes.py` contains reusable tree node structures for the parser.
- `symbol_table.py` stores identifier metadata used during analysis.
- `tac_generator.py` converts AST structures into TAC instructions.
- `optimizer.py` applies optimization passes to TAC output.
- `visualizer.py` renders AST and intermediate forms for presentation.

## Current Status

The repository currently contains only the project skeleton and placeholder interfaces. The implementation logic will be added in later development stages.
