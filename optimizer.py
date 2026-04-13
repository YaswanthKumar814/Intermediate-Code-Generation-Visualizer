"""Simple TAC optimizer for educational compiler demonstrations."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set, Tuple

from tac_generator import TACInstruction


class TACOptimizer:
    """Applies optimization passes to three-address code."""

    COMMUTATIVE_OPS = {"+", "*"}
    ARITHMETIC_OPS = {"+", "-", "*", "/"}

    def optimize(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Run all optimization passes in a simple, stable order."""
        optimized = self.constant_folding(instructions)
        optimized = self.common_subexpression_elimination(optimized)
        optimized = self.dead_code_elimination(optimized)
        return optimized

    def constant_folding(self, instructions: List[TACInstruction]) -> List[TACInstruction]:
        """Fold arithmetic instructions whose operands are known constants."""
        constants: Dict[str, Any] = {}
        optimized: List[TACInstruction] = []

        for instruction in instructions:
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
                raise ZeroDivisionError("Division by zero during constant folding.")
            return left // right
        raise ValueError(f"Unsupported operator: {operator}")

    def _is_number(self, value: Any) -> bool:
        """Return True when the operand is an integer constant."""
        return isinstance(value, int)


def format_tac(instructions: Iterable[TACInstruction]) -> str:
    """Return a printable multi-line representation of TAC instructions."""
    return "\n".join(str(instruction) for instruction in instructions)


if __name__ == "__main__":
    before_tac = [
        TACInstruction("a", 5),
        TACInstruction("b", 10),
        TACInstruction("t1", 2, "+", 3),
        TACInstruction("t2", "a", "+", "b"),
        TACInstruction("t3", "a", "+", "b"),
        TACInstruction("unused", "t1"),
        TACInstruction("c", "t3"),
        TACInstruction("print", "c"),
    ]

    optimizer = TACOptimizer()
    after_tac = optimizer.optimize(before_tac)

    print("BEFORE TAC")
    print(format_tac(before_tac))
    print("\nAFTER TAC")
    print(format_tac(after_tac))
