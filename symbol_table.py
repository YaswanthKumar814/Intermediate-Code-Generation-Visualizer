"""Symbol table skeleton for tracking identifiers in the custom language."""

from dataclasses import dataclass
from typing import Any


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
        raise NotImplementedError("Symbol insertion will be implemented later.")

    def lookup(self, name: str) -> Symbol | None:
        """Fetch a symbol definition by identifier name."""
        raise NotImplementedError("Symbol lookup will be implemented later.")

    def update(self, name: str, value: Any) -> None:
        """Update the stored value of an existing symbol."""
        raise NotImplementedError("Symbol updates will be implemented later.")
