"""Three-address code generation for the compiler visualizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List

from ast_nodes import ASTNode


@dataclass(slots=True)
class TACInstruction:
    """Represents a single three-address code instruction."""

    target: str
    arg1: Any
    operator: str | None = None
    arg2: Any = None

    def __str__(self) -> str:
        """Render the instruction in a compact classroom-friendly format."""
        if self.operator == "label":
            return f"{self.target}:"
        if self.operator == "goto":
            return f"goto {self.arg1}"
        if self.operator == "if_false":
            return f"if_false {self.arg1} goto {self.arg2}"
        if self.operator is None:
            return f"{self.target} = {self.arg1}"
        return f"{self.target} = {self.arg1} {self.operator} {self.arg2}"


class TACGenerator:
    """Converts an abstract syntax tree into three-address code."""

    ARITHMETIC_OPS = {"+", "-", "*", "/"}

    def __init__(self) -> None:
        """Initialize temporary state and the generated instruction list."""
        self.temp_count = 0
        self.label_count = 0
        self.instructions: List[TACInstruction] = []

    def generate(self, ast_root: ASTNode) -> List[TACInstruction]:
        """Generate TAC instructions from the AST root node."""
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []

        if ast_root.type != "Program":
            raise ValueError("TAC generation expects a Program node as the AST root.")

        for statement in ast_root.children:
            self._generate_statement(statement)

        return self.instructions

    def new_temp(self) -> str:
        """Create a fresh temporary variable name."""
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self) -> str:
        """Create a fresh label name for control flow."""
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(
        self,
        target: str,
        arg1: Any,
        operator: str | None = None,
        arg2: Any = None,
    ) -> TACInstruction:
        """Append a TAC instruction to the instruction list."""
        instruction = TACInstruction(target=target, arg1=arg1, operator=operator, arg2=arg2)
        self.instructions.append(instruction)
        return instruction

    def _generate_statement(self, node: ASTNode) -> None:
        """Dispatch TAC generation for statement-level AST nodes."""
        if node.type == "VarDecl":
            if node.children:
                value = self._generate_expression(node.children[0])
                self.emit(node.value, value)
            return

        if node.type == "Assign":
            value = self._generate_expression(node.children[0])
            self.emit(node.value, value)
            return

        if node.type == "Print":
            value = self._generate_expression(node.children[0])
            self.emit("print", value)
            return

        if node.type == "Block":
            for statement in node.children:
                self._generate_statement(statement)
            return

        if node.type == "IF":
            false_label = self.new_label()
            condition = self._generate_expression(node.children[0])
            self.emit("", condition, "if_false", false_label)
            self._generate_statement(node.children[1])
            self.emit(false_label, None, "label")
            return

        if node.type == "IF_ELSE":
            false_label = self.new_label()
            end_label = self.new_label()
            condition = self._generate_expression(node.children[0])
            self.emit("", condition, "if_false", false_label)
            self._generate_statement(node.children[1])
            self.emit("", end_label, "goto")
            self.emit(false_label, None, "label")
            self._generate_statement(node.children[2])
            self.emit(end_label, None, "label")
            return

        if node.type == "WHILE":
            start_label = self.new_label()
            end_label = self.new_label()
            self.emit(start_label, None, "label")
            condition = self._generate_expression(node.children[0])
            self.emit("", condition, "if_false", end_label)
            self._generate_statement(node.children[1])
            self.emit("", start_label, "goto")
            self.emit(end_label, None, "label")
            return

        raise ValueError(f"Unsupported statement node: {node.type}")

    def _generate_expression(self, node: ASTNode) -> Any:
        """Generate TAC for an expression and return its resulting operand."""
        if node.type == "Number":
            return node.value

        if node.type == "Identifier":
            return node.value

        if node.type == "BinOp":
            left = self._generate_expression(node.children[0])
            right = self._generate_expression(node.children[1])
            temp = self.new_temp()
            if node.value in self.ARITHMETIC_OPS:
                self.emit(temp, left, node.value, right)
            else:
                self.emit(temp, f"{left} {node.value} {right}")
            return temp

        raise ValueError(f"Unsupported expression node: {node.type}")


if __name__ == "__main__":
    from parser import CompilerParser

    sample_code = """
    int a = 3;
    while (a > 0) {
        print(a);
        a = a - 1;
    }
    """

    parser = CompilerParser()
    ast_root = parser.parse(sample_code)

    generator = TACGenerator()
    tac = generator.generate(ast_root)

    print("Input Program:")
    print(sample_code.strip())
    print("\nGenerated Three-Address Code:")
    for instruction in tac:
        print(instruction)

    print("\nExample Output:")
    print("a = 3")
    print("L1:")
    print("t1 = a > 0")
    print("if_false t1 goto L2")
    print("print = a")
    print("t2 = a - 1")
    print("a = t2")
    print("goto L1")
    print("L2:")
