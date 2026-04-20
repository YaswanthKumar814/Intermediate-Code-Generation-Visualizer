"""Graphviz-based AST visualizer for the compiler project."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from graphviz import Digraph
from graphviz.backend import ExecutableNotFound

from ast_nodes import ASTNode


class ASTVisualizer:
    """Builds and renders a Graphviz tree for an abstract syntax tree."""

    def __init__(self) -> None:
        """Initialize node numbering used for unique graph identifiers."""
        self._node_count = 0

    def build_graph(self, ast_root: ASTNode) -> Digraph:
        """Construct a Graphviz directed graph from the AST root."""
        self._node_count = 0

        graph = Digraph(comment="Abstract Syntax Tree", format="png")
        graph.attr(rankdir="TB")
        graph.attr("node", shape="box", style="rounded,filled", fillcolor="lightyellow")

        self._add_ast_node(graph, ast_root)
        return graph

    def render_ast(self, ast_root: ASTNode, output_path: str | Path) -> Path:
        """Render the AST graph to a file and return the generated file path."""
        self._ensure_graphviz_available()
        graph = self.build_graph(ast_root)
        output_base = Path(output_path)
        output_base.parent.mkdir(parents=True, exist_ok=True)
        rendered_path = graph.render(filename=output_base.stem, directory=output_base.parent, cleanup=True)
        return Path(rendered_path)

    def _add_ast_node(self, graph: Digraph, node: ASTNode) -> str:
        """Recursively add AST nodes and edges to the Graphviz graph."""
        if node is None:
            node_id = f"node_{self._node_count}"
            self._node_count += 1
            graph.node(node_id, "None")
            return node_id

        node_id = f"node_{self._node_count}"
        self._node_count += 1

        graph.node(node_id, self._format_label(node))

        for child in node.children:
            if child is None:
                continue
            child_id = self._add_ast_node(graph, child)
            graph.edge(node_id, child_id)

        return node_id

    def _format_label(self, node: ASTNode) -> str:
        """Create a clear label for a visualized AST node."""
        if node is None:
            return "None"
        if node.value is None:
            return node.type
        return f"{node.type}\n({node.value})"

    def _ensure_graphviz_available(self) -> None:
        """Ensure the Graphviz 'dot' executable is available, especially on Windows."""
        if shutil.which("dot"):
            return

        for path in self._candidate_graphviz_bins():
            dot_exe = path / "dot.exe"
            if dot_exe.exists():
                os.environ["PATH"] = f"{path}{os.pathsep}{os.environ.get('PATH', '')}"
                return

        raise ExecutableNotFound(
            "Graphviz executable not found. Install Graphviz system software and add its 'bin' folder to PATH."
        )

    def _candidate_graphviz_bins(self) -> list[Path]:
        """Return common Windows install locations for Graphviz."""
        candidates: list[Path] = []
        roots = [
            Path(r"C:\Program Files"),
            Path(r"C:\Program Files (x86)"),
        ]

        for root in roots:
            direct_bin = root / "Graphviz" / "bin"
            if direct_bin.exists():
                candidates.append(direct_bin)

            if root.exists():
                for match in root.glob("Graphviz*"):
                    bin_path = match / "bin"
                    if bin_path.exists():
                        candidates.append(bin_path)

        return candidates


if __name__ == "__main__":
    sample_ast = ASTNode(
        "Program",
        children=[
            ASTNode("VarDecl", value="a", children=[ASTNode("Number", value=5)]),
            ASTNode(
                "Assign",
                value="b",
                children=[
                    ASTNode(
                        "BinOp",
                        value="+",
                        children=[
                            ASTNode("Identifier", value="a"),
                            ASTNode("Number", value=10),
                        ],
                    )
                ],
            ),
            ASTNode("Print", children=[ASTNode("Identifier", value="b")]),
        ],
    )

    visualizer = ASTVisualizer()
    try:
        output_file = visualizer.render_ast(sample_ast, "ast_output")
        print(f"AST visualization generated: {output_file}")
    except ExecutableNotFound as error:
        print(error)
