"""Flask web UI for the Intermediate Code Generation Visualizer."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from flask import Flask, render_template, request, send_from_directory, url_for
from graphviz.backend import ExecutableNotFound

from optimizer import TACOptimizer, format_tac
from parser import CompilerParser
from tac_generator import TACGenerator
from visualizer import ASTVisualizer

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

DEFAULT_SOURCE = """int a = 5;
int b = 10;
int c;
c = a + b * 2;
print(c);"""

MAX_SOURCE_LENGTH = 10000

app = Flask(__name__)


def run_pipeline(source_code: str) -> dict[str, str | None]:
    """Execute the compiler pipeline and return UI-friendly results."""
    parser = CompilerParser()
    tac_generator = TACGenerator()
    optimizer = TACOptimizer()
    visualizer = ASTVisualizer()

    ast_root = parser.parse(source_code)
    tac_before = tac_generator.generate(ast_root)
    tac_after = optimizer.optimize(tac_before)

    ast_image_url: str | None = None
    warning: str | None = None

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    image_stem = f"ast_{uuid4().hex}"

    try:
        image_path = visualizer.render_ast(ast_root, OUTPUT_DIR / image_stem)
        ast_image_url = url_for("serve_output", filename=image_path.name)
    except ExecutableNotFound:
        warning = (
            "Graphviz executable not found. Install Graphviz system binaries and add them to PATH "
            "to generate the AST image."
        )

    return {
        "ast_image_url": ast_image_url,
        "ast_json": ast_root.to_dict().__repr__(),
        "tac_before": format_tac(tac_before),
        "tac_after": format_tac(tac_after),
        "warning": warning,
    }


@app.get("/")
def index():
    """Render the main page with sample code."""
    return render_template(
        "index.html",
        source_code=DEFAULT_SOURCE,
        result=None,
        error=None,
    )


@app.post("/run")
def run_code():
    """Accept source code input and render pipeline results."""
    source_code = request.form.get("source_code", "")

    if not source_code.strip():
        return render_template(
            "index.html",
            source_code=source_code,
            result=None,
            error="Please enter source code before running the visualizer.",
        )

    if len(source_code) > MAX_SOURCE_LENGTH:
        return render_template(
            "index.html",
            source_code=source_code,
            result=None,
            error=f"Input is too large. Please keep the program under {MAX_SOURCE_LENGTH} characters.",
        )

    try:
        result = run_pipeline(source_code)
        return render_template(
            "index.html",
            source_code=source_code,
            result=result,
            error=None,
        )
    except (SyntaxError, ValueError, ZeroDivisionError) as error:
        return render_template(
            "index.html",
            source_code=source_code,
            result=None,
            error=str(error),
        )


@app.get("/outputs/<path:filename>")
def serve_output(filename: str):
    """Serve generated AST image files."""
    return send_from_directory(OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
