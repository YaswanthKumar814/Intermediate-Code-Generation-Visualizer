"""Main entry point for the Intermediate Code Generation Visualizer."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from graphviz.backend import ExecutableNotFound

from lexer import CompilerLexer
from optimizer import TACOptimizer, format_tac
from parser import CompilerParser
from tac_generator import TACGenerator
from visualizer import ASTVisualizer

SAMPLE_CODE = """
int a = 5;
int b = 10;
int c;
c = a + b * 2;
print(c);
""".strip()


class CompilerPipeline:
    """Coordinates the compiler stages from source input to visualization."""

    def __init__(self) -> None:
        """Initialize all compiler components."""
        self.lexer = CompilerLexer()
        self.parser = CompilerParser()
        self.tac_generator = TACGenerator()
        self.optimizer = TACOptimizer()
        self.visualizer = ASTVisualizer()

    def run(self, source_code: str) -> None:
        """Execute the full compiler pipeline and print each stage."""
        print_section("SOURCE CODE")
        print(source_code)

        tokens = self.lexer.tokenize(source_code)
        print_section("TOKENS")
        print(format_tokens(tokens))

        ast_root = self.parser.parse(source_code)
        print_section("AST")
        print(json.dumps(ast_root.to_dict(), indent=2))

        tac_before = self.tac_generator.generate(ast_root)
        print_section("TAC BEFORE OPTIMIZATION")
        print(format_tac(tac_before))

        tac_after = self.optimizer.optimize(tac_before)
        print_section("TAC AFTER OPTIMIZATION")
        print(format_tac(tac_after))

        output_dir = Path(__file__).resolve().parent / "outputs"
        output_dir.mkdir(exist_ok=True)

        try:
            ast_image = self.visualizer.render_ast(ast_root, output_dir / "ast_visualization")
            print_section("VISUALIZATION")
            print(f"AST graph saved to: {ast_image}")
        except ExecutableNotFound:
            print_section("VISUALIZATION")
            print("Graphviz executable not found. Install Graphviz system binaries to render the AST image.")


def load_source_from_argument() -> str:
    """Load source code from a file path argument if one is provided."""
    if len(sys.argv) < 2:
        return SAMPLE_CODE

    source_path = Path(sys.argv[1]).resolve()
    return source_path.read_text(encoding="utf-8")


def format_tokens(tokens: list) -> str:
    """Return a readable multi-line token listing."""
    lines = []
    for token in tokens:
        lines.append(
            f"{token.token_type:<10} value={token.value!r:<8} line={token.line:<2} column={token.column}"
        )
    return "\n".join(lines)


def print_section(title: str) -> None:
    """Print a simple section header for console output."""
    print(f"\n{'=' * 12} {title} {'=' * 12}")


def main() -> None:
    """Run the compiler visualizer using sample code or a provided file."""
    try:
        source_code = load_source_from_argument()
        pipeline = CompilerPipeline()
        pipeline.run(source_code)
    except FileNotFoundError as error:
        print(f"Input file not found: {error.filename}")
    except (SyntaxError, ValueError, ZeroDivisionError) as error:
        print(f"Compilation failed: {error}")


if __name__ == "__main__":
    main()
