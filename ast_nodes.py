"""Abstract syntax tree node definitions for the compiler visualizer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ASTNode:
    """Represents a node in the abstract syntax tree."""

    type: str
    value: Any = None
    children: List["ASTNode"] = field(default_factory=list)

    @property
    def node_type(self) -> str:
        """Provide compatibility with code that refers to node_type."""
        return self.type

    def add_child(self, child: "ASTNode") -> None:
        """Attach a child node to the current AST node."""
        self.children.append(child)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the AST into a nested dictionary."""
        return {
            "type": self.type,
            "value": self.value,
            "children": [child.to_dict() for child in self.children],
        }
