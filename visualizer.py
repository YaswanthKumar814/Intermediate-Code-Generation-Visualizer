"""Graphviz-based AST visualizer for the compiler project."""

from __future__ import annotations

from pathlib import Path

from graphviz import Digraph

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
        graph = self.build_graph(ast_root)
        output_base = Path(output_path)
        rendered_path = graph.render(filename=output_base.stem, directory=output_base.parent, cleanup=True)
        return Path(rendered_path)

    def _add_ast_node(self, graph: Digraph, node: ASTNode) -> str:
        """Recursively add AST nodes and edges to the Graphviz graph."""
        node_id = f"node_{self._node_count}"
        self._node_count += 1

        graph.node(node_id, self._format_label(node))

        for child in node.children:
            child_id = self._add_ast_node(graph, child)
            graph.edge(node_id, child_id)

        return node_id

    def _format_label(self, node: ASTNode) -> str:
        """Create a clear label for a visualized AST node."""
        if node.value is None:
            return node.type
        return f"{node.type}\n({node.value})"


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
    output_file = visualizer.render_ast(sample_ast, "ast_output")
    print(f"AST visualization generated: {output_file}")
