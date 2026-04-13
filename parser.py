"""PLY-based syntax analyzer that builds an AST from source code."""

from __future__ import annotations

from typing import Optional

import ply.yacc as yacc

from ast_nodes import ASTNode
from lexer import CompilerLexer


class CompilerParser:
    """Builds an abstract syntax tree for the supported mini language."""

    tokens = CompilerLexer.tokens

    precedence = (
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
    )

    def __init__(self) -> None:
        """Initialize lexer and parser instances."""
        self.lexer = CompilerLexer()
        self.parser = yacc.yacc(module=self, write_tables=False, debug=False)

    def parse(self, source_code: str) -> ASTNode:
        """Parse source code and return the root AST node."""
        self.lexer.lexer.lineno = 1
        return self.parser.parse(source_code, lexer=self.lexer.lexer)

    def p_program(self, production) -> None:
        """program : statement_list"""
        production[0] = ASTNode("Program", children=production[1])

    def p_statement_list_multiple(self, production) -> None:
        """statement_list : statement_list statement"""
        production[0] = production[1] + [production[2]]

    def p_statement_list_single(self, production) -> None:
        """statement_list : statement"""
        production[0] = [production[1]]

    def p_statement(self, production) -> None:
        """statement : declaration_statement
                     | assignment_statement
                     | print_statement"""
        production[0] = production[1]

    def p_declaration_statement_initialized(self, production) -> None:
        """declaration_statement : INT IDENTIFIER ASSIGN expression SEMICOLON"""
        production[0] = ASTNode(
            "VarDecl",
            value=production[2],
            children=[production[4]],
        )

    def p_declaration_statement_uninitialized(self, production) -> None:
        """declaration_statement : INT IDENTIFIER SEMICOLON"""
        production[0] = ASTNode("VarDecl", value=production[2], children=[])

    def p_assignment_statement(self, production) -> None:
        """assignment_statement : IDENTIFIER ASSIGN expression SEMICOLON"""
        production[0] = ASTNode(
            "Assign",
            value=production[1],
            children=[production[3]],
        )

    def p_print_statement(self, production) -> None:
        """print_statement : PRINT LPAREN expression RPAREN SEMICOLON"""
        production[0] = ASTNode("Print", children=[production[3]])

    def p_expression_binary(self, production) -> None:
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression"""
        production[0] = ASTNode(
            "BinOp",
            value=production[2],
            children=[production[1], production[3]],
        )

    def p_expression_group(self, production) -> None:
        """expression : LPAREN expression RPAREN"""
        production[0] = production[2]

    def p_expression_number(self, production) -> None:
        """expression : NUMBER"""
        production[0] = ASTNode("Number", value=production[1])

    def p_expression_identifier(self, production) -> None:
        """expression : IDENTIFIER"""
        production[0] = ASTNode("Identifier", value=production[1])

    def p_error(self, production: Optional[object]) -> None:
        """Raise a clear syntax error with token location information."""
        if production is None:
            raise SyntaxError("Syntax error: unexpected end of input")

        column = self.lexer.find_column(production)
        raise SyntaxError(
            f"Syntax error: unexpected token {production.value!r} "
            f"at line {production.lineno}, column {column}"
        )


if __name__ == "__main__":
    sample_code = """
    int a = 5;
    int b;
    b = a + 3 * 2;
    print(b);
    """

    parser = CompilerParser()
    ast_root = parser.parse(sample_code)
    print(ast_root.to_dict())
