"""Simple TAC optimizer for educational compiler demonstrations."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set, Tuple

from tac_generator import TACInstruction


class DivisionByZeroError(ValueError):
    """Raised when constant folding detects division by zero."""


class TACOptimizer:
    """Applies optimization passes to three-address code."""

    COMMUTATIVE_OPS = {"+", "*"}
    ARITHMETIC_OPS = {"+", "-", "*", "/"}
    CONTROL_FLOW_OPS = {"label", "goto", "if_false"}

    def __init__(self) -> None:
        """Initialize optimizer state."""
        self.warnings: List[str] = []

    def optimize(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Run all optimization passes in a simple, stable order."""
        self.warnings = []
        if self._has_control_flow(instructions):
            optimized: List[TACInstruction] = []
            for block in self._split_basic_blocks(instructions):
                optimized.extend(self._optimize_basic_block(block))
            return optimized

        optimized = self.constant_folding(instructions)
        optimized = self.common_subexpression_elimination(optimized)
        optimized = self.dead_code_elimination(optimized)
        return optimized

    def constant_folding(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Fold arithmetic instructions whose operands are known constants."""
        constants: Dict[str, Any] = {}
        optimized: List[TACInstruction] = []

        for instruction in instructions:
            if instruction.operator in self.CONTROL_FLOW_OPS:
                optimized.append(instruction)
                constants.clear()
                continue

            if instruction.target == "print":
                value = self._resolve_operand(instruction.arg1, constants)
                optimized.append(TACInstruction("print", value))
                continue

            if instruction.operator is None:
                value = self._resolve_operand(instruction.arg1, constants)
                optimized.append(TACInstruction(instruction.target, value))
                if self._is_number(value):
                    constants[instruction.target] = value
                else:
                    constants.pop(instruction.target, None)
                continue

            left = self._resolve_operand(instruction.arg1, constants)
            right = self._resolve_operand(instruction.arg2, constants)

            if self._is_number(left) and self._is_number(right):
                result = self._evaluate(left, instruction.operator, right)
                optimized.append(TACInstruction(instruction.target, result))
                constants[instruction.target] = result
            else:
                optimized.append(TACInstruction(instruction.target, left, instruction.operator, right))
                constants.pop(instruction.target, None)

        return optimized

    def dead_code_elimination(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Remove assignments whose results are never used."""
        if self._has_control_flow(instructions):
            return list(instructions)

        live_variables: Set[str] = set()
        optimized_reversed: List[TACInstruction] = []

        for instruction in reversed(instructions):
            if instruction.target == "print":
                optimized_reversed.append(instruction)
                live_variables.update(self._used_names(instruction))
                continue

            if instruction.target not in live_variables:
                continue

            optimized_reversed.append(instruction)
            live_variables.discard(instruction.target)
            live_variables.update(self._used_names(instruction))

        optimized_reversed.reverse()
        return optimized_reversed

    def common_subexpression_elimination(
        self, instructions: List[TACInstruction]
    ) -> List[TACInstruction]:
        """Replace repeated arithmetic expressions with previously computed results."""
        available_expressions: Dict[Tuple[Any, str, Any], str] = {}
        optimized: List[TACInstruction] = []

        for instruction in instructions:
            if instruction.operator in self.CONTROL_FLOW_OPS:
                optimized.append(instruction)
                available_expressions.clear()
                continue

            if instruction.target == "print":
                optimized.append(instruction)
                continue

            self._invalidate_expressions(available_expressions, instruction.target)

            if instruction.operator is None:
                optimized.append(instruction)
                continue

            expression_key = self._expression_key(
                instruction.arg1, instruction.operator, instruction.arg2
            )

            if expression_key in available_expressions:
                previous_result = available_expressions[expression_key]
                optimized.append(TACInstruction(instruction.target, previous_result))
            else:
                optimized.append(instruction)
                available_expressions[expression_key] = instruction.target

        return optimized

    def _resolve_operand(self, operand: Any, constants: Dict[str, Any]) -> Any:
        """Replace variable operands with known constants when possible."""
        if isinstance(operand, str) and operand in constants:
            return constants[operand]
        return operand

    def _used_names(self, instruction: TACInstruction) -> Set[str]:
        """Collect variable-like operands used by an instruction."""
        used: Set[str] = set()
        if instruction.operator == "goto" or instruction.operator == "label":
            return used
        if instruction.operator == "if_false":
            if isinstance(instruction.arg1, str) and instruction.arg1 != "print":
                used.add(instruction.arg1)
            return used
        for operand in (instruction.arg1, instruction.arg2):
            if isinstance(operand, str) and operand != "print":
                used.add(operand)
        return used

    def _expression_key(self, left: Any, operator: str, right: Any) -> Tuple[Any, str, Any]:
        """Build a canonical key for arithmetic expressions."""
        if operator in self.COMMUTATIVE_OPS:
            ordered = tuple(sorted((left, right), key=str))
            return ordered[0], operator, ordered[1]
        return left, operator, right

    def _invalidate_expressions(
        self, expressions: Dict[Tuple[Any, str, Any], str], assigned_name: str
    ) -> None:
        """Drop cached expressions that depend on a variable that changed."""
        if assigned_name == "print":
            return

        stale_keys = [
            key
            for key, result_name in expressions.items()
            if assigned_name == result_name or assigned_name == key[0] or assigned_name == key[2]
        ]
        for key in stale_keys:
            expressions.pop(key, None)

    def _evaluate(self, left: int, operator: str, right: int) -> int:
        """Evaluate a constant arithmetic expression."""
        if operator == "+":
            return left + right
        if operator == "-":
            return left - right
        if operator == "*":
            return left * right
        if operator == "/":
            if right == 0:
                raise DivisionByZeroError("Error: Division by zero")
            return self._truncate_toward_zero(left, right)
        raise ValueError(f"Unsupported operator: {operator}")

    def _is_number(self, value: Any) -> bool:
        """Return True when the operand is an integer constant."""
        return isinstance(value, int)

    def _truncate_toward_zero(self, left: int, right: int) -> int:
        """Perform C-like integer division by truncating toward zero."""
        quotient = abs(left) // abs(right)
        return quotient if (left >= 0) == (right >= 0) else -quotient

    def _has_control_flow(self, instructions: Iterable[TACInstruction]) -> bool:
        """Return True when TAC contains labels or jumps."""
        return any(instruction.operator in self.CONTROL_FLOW_OPS for instruction in instructions)

    def _split_basic_blocks(self, instructions: List[TACInstruction]) -> List[List[TACInstruction]]:
        """Split TAC into basic blocks at labels and jump boundaries."""
        blocks: List[List[TACInstruction]] = []
        current_block: List[TACInstruction] = []

        for instruction in instructions:
            if instruction.operator == "label" and current_block:
                blocks.append(current_block)
                current_block = []

            current_block.append(instruction)

            if instruction.operator in {"goto", "if_false"}:
                blocks.append(current_block)
                current_block = []

        if current_block:
            blocks.append(current_block)

        return blocks

    def _optimize_basic_block(self, block: List[TACInstruction]) -> List[TACInstruction]:
        """Apply only straight-line-safe optimizations inside one basic block."""
        leading_labels: List[TACInstruction] = []
        middle_start = 0

        while middle_start < len(block) and block[middle_start].operator == "label":
            leading_labels.append(block[middle_start])
            middle_start += 1

        trailing_control: List[TACInstruction] = []
        middle_end = len(block)
        if middle_start < len(block) and block[-1].operator in {"goto", "if_false"}:
            trailing_control = [block[-1]]
            middle_end -= 1

        middle = block[middle_start:middle_end]
        optimized_middle = self.constant_folding(middle)
        optimized_middle = self.common_subexpression_elimination(optimized_middle)

        return leading_labels + optimized_middle + trailing_control


def format_tac(instructions: Iterable[TACInstruction]) -> str:
    """Return a printable multi-line representation of TAC instructions."""
    return "\n".join(str(instruction) for instruction in instructions)


if __name__ == "__main__":
    before_tac = [
        TACInstruction("t1", -3, "/", 2),
        TACInstruction("t2", 10, "/", 0),
        TACInstruction("print", "t1"),
    ]

    optimizer = TACOptimizer()

    print("BEFORE TAC")
    print(format_tac(before_tac))
    try:
        after_tac = optimizer.optimize(before_tac)
        print("\nAFTER TAC")
        print(format_tac(after_tac))
    except DivisionByZeroError as error:
        print(f"\nOptimization failed: {error}")
