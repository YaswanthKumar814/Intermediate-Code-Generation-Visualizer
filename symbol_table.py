"""Symbol table and semantic analysis for the custom language."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ast_nodes import ASTNode


class SemanticError(ValueError):
    """Raised when semantic validation fails."""


@dataclass(slots=True)
class Symbol:
    """Stores metadata associated with a declared identifier."""

    name: str
    symbol_type: str
    value: Any = None


class SymbolTable:
    """Provides scoped storage for variables and their attributes."""

    def __init__(self) -> None:
        """Initialize the symbol table storage."""
        self._symbols: dict[str, Symbol] = {}

    def define(self, name: str, symbol_type: str, value: Any = None) -> None:
        """Insert a new symbol into the table."""
        if name in self._symbols:
            raise SemanticError(f"Semantic Error: Variable '{name}' redeclared")
        self._symbols[name] = Symbol(name=name, symbol_type=symbol_type, value=value)

    def lookup(self, name: str) -> Symbol | None:
        """Fetch a symbol definition by identifier name."""
        return self._symbols.get(name)

    def update(self, name: str, value: Any) -> None:
        """Update the stored value of an existing symbol."""
        symbol = self.lookup(name)
        if symbol is None:
            raise SemanticError(f"Semantic Error: Variable '{name}' not declared")
        symbol.value = value


class SemanticAnalyzer:
    """Validates declarations and variable usage against the symbol table."""

    def __init__(self) -> None:
        """Initialize the analyzer with a fresh symbol table."""
        self.symbol_table = SymbolTable()

    def validate(self, ast_root: ASTNode) -> SymbolTable:
        """Walk the AST and raise SemanticError for invalid programs."""
        if ast_root.type != "Program":
            raise SemanticError("Semantic Error: Invalid program structure")

        for statement in ast_root.children:
            self._validate_statement(statement)

        return self.symbol_table

    def _validate_statement(self, node: ASTNode) -> None:
        """Validate a single statement node."""
        if node.type == "VarDecl":
            if node.children:
                self._validate_expression(node.children[0])
            self.symbol_table.define(node.value, "int")
            return

        if node.type == "Assign":
            if self.symbol_table.lookup(node.value) is None:
                raise SemanticError(f"Semantic Error: Variable '{node.value}' not declared")
            self._validate_expression(node.children[0])
            self.symbol_table.update(node.value, None)
            return

        if node.type == "Print":
            self._validate_expression(node.children[0])
            return

        raise SemanticError(f"Semantic Error: Unsupported statement type '{node.type}'")

    def _validate_expression(self, node: ASTNode) -> None:
        """Validate identifiers used inside expressions."""
        if node.type == "Number":
            return

        if node.type == "Identifier":
            if self.symbol_table.lookup(node.value) is None:
                raise SemanticError(f"Semantic Error: Variable '{node.value}' not declared")
            return

        if node.type == "BinOp":
            self._validate_expression(node.children[0])
            self._validate_expression(node.children[1])
            return

        raise SemanticError(f"Semantic Error: Unsupported expression type '{node.type}'")
