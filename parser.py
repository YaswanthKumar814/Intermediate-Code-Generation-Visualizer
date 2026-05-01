"""PLY-based syntax analyzer that builds an AST from source code."""

from __future__ import annotations

from typing import Optional

import ply.yacc as yacc

from ast_nodes import ASTNode
from lexer import CompilerLexer
from symbol_table import SemanticAnalyzer, SemanticError


class CompilerParser:
    """Builds an abstract syntax tree for the supported mini language."""

    tokens = CompilerLexer.tokens

    precedence = (
        ("left", "OR"),
        ("left", "AND"),
        ("left", "EQ", "NE"),
        ("left", "GT", "LT", "GE", "LE"),
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
        ("right", "UMINUS"),
    )

    def __init__(self) -> None:
        """Initialize lexer and parser instances."""
        self.lexer = CompilerLexer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.parser = yacc.yacc(module=self, write_tables=False, debug=False)

    def parse(self, source_code: str) -> ASTNode:
        """Parse source code and return the root AST node."""
        self.lexer.lexer.lineno = 1
        ast_root = self.parser.parse(source_code, lexer=self.lexer.lexer)
        if ast_root is None:
            ast_root = ASTNode("Program", children=[])
        ast_root = self._sanitize_ast(ast_root)
        self.semantic_analyzer = SemanticAnalyzer()
        self._validate_semantics(ast_root)
        return ast_root

    def p_program(self, production) -> None:
        """program : statement_list"""
        production[0] = ASTNode("Program", children=production[1])

    def p_program_empty(self, production) -> None:
        """program : empty"""
        production[0] = ASTNode("Program", children=[])

    def p_statement_list_multiple(self, production) -> None:
        """statement_list : statement_list statement"""
        production[0] = production[1] + [production[2]]

    def p_statement_list_single(self, production) -> None:
        """statement_list : statement"""
        production[0] = [production[1]]

    def p_statement(self, production) -> None:
        """statement : declaration_statement
                     | assignment_statement
                     | print_statement
                     | goto_statement
                     | label_statement
                     | if_statement
                     | while_statement
                     | for_statement"""
        production[0] = production[1]

    def p_block_nonempty(self, production) -> None:
        """block : LBRACE statement_list RBRACE"""
        production[0] = ASTNode("Block", children=production[2])

    def p_block_empty(self, production) -> None:
        """block : LBRACE RBRACE"""
        production[0] = ASTNode("Block", children=[])

    def p_declaration_statement(self, production) -> None:
        """declaration_statement : INT declarator_list SEMICOLON"""
        production[0] = self._declaration_result(production[2])

    def p_declarator_list_multiple(self, production) -> None:
        """declarator_list : declarator_list COMMA declarator"""
        production[0] = production[1] + [production[3]]

    def p_declarator_list_single(self, production) -> None:
        """declarator_list : declarator"""
        production[0] = [production[1]]

    def p_declarator_initialized(self, production) -> None:
        """declarator : IDENTIFIER ASSIGN expression"""
        production[0] = ASTNode("VarDecl", value=production[1], children=[production[3]])

    def p_declarator_uninitialized(self, production) -> None:
        """declarator : IDENTIFIER"""
        production[0] = ASTNode("VarDecl", value=production[1], children=[])

    def p_assignment_statement(self, production) -> None:
        """assignment_statement : IDENTIFIER ASSIGN expression SEMICOLON"""
        production[0] = ASTNode(
            "Assign",
            value=production[1],
            children=[production[3]],
        )

    def p_for_init_declaration(self, production) -> None:
        """for_init : INT declarator_list"""
        production[0] = self._declaration_result(production[2])

    def p_for_init_assignment(self, production) -> None:
        """for_init : IDENTIFIER ASSIGN expression"""
        production[0] = ASTNode("Assign", value=production[1], children=[production[3]])

    def p_for_init_empty(self, production) -> None:
        """for_init : empty"""
        production[0] = ASTNode("Empty")

    def p_for_condition_expression(self, production) -> None:
        """for_condition : expression"""
        production[0] = production[1]

    def p_for_condition_empty(self, production) -> None:
        """for_condition : empty"""
        production[0] = ASTNode("Empty")

    def p_for_update_assignment(self, production) -> None:
        """for_update : IDENTIFIER ASSIGN expression"""
        production[0] = ASTNode("Assign", value=production[1], children=[production[3]])

    def p_for_update_empty(self, production) -> None:
        """for_update : empty"""
        production[0] = ASTNode("Empty")

    def p_print_statement(self, production) -> None:
        """print_statement : PRINT LPAREN expression RPAREN SEMICOLON"""
        production[0] = ASTNode("Print", children=[production[3]])

    def p_goto_statement(self, production) -> None:
        """goto_statement : GOTO IDENTIFIER SEMICOLON"""
        production[0] = ASTNode("Goto", value=production[2])

    def p_label_statement(self, production) -> None:
        """label_statement : IDENTIFIER COLON"""
        production[0] = ASTNode("Label", value=production[1])

    def p_if_statement(self, production) -> None:
        """if_statement : IF LPAREN expression RPAREN block
                        | IF LPAREN expression RPAREN block ELSE block"""
        if len(production) == 6:
            production[0] = ASTNode("IF", children=[production[3], production[5]])
        else:
            production[0] = ASTNode("IF_ELSE", children=[production[3], production[5], production[7]])

    def p_while_statement(self, production) -> None:
        """while_statement : WHILE LPAREN expression RPAREN block"""
        production[0] = ASTNode("WHILE", children=[production[3], production[5]])

    def p_for_statement(self, production) -> None:
        """for_statement : FOR LPAREN for_init SEMICOLON for_condition SEMICOLON for_update RPAREN block"""
        production[0] = ASTNode("FOR", children=[production[3], production[5], production[7], production[9]])

    def p_expression_binary(self, production) -> None:
        """expression : expression PLUS expression
                      | expression MINUS expression
                      | expression TIMES expression
                      | expression DIVIDE expression
                      | expression GT expression
                      | expression LT expression
                      | expression GE expression
                      | expression LE expression
                      | expression EQ expression
                      | expression NE expression
                      | expression AND expression
                      | expression OR expression"""
        production[0] = ASTNode(
            "BinOp",
            value=production[2],
            children=[production[1], production[3]],
        )

    def p_expression_uminus(self, production) -> None:
        """expression : MINUS expression %prec UMINUS"""
        production[0] = ASTNode(
            "BinOp",
            value="-",
            children=[ASTNode("Number", value=0), production[2]],
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

    def p_empty(self, production) -> None:
        """empty :"""
        production[0] = None

    def p_error(self, production: Optional[object]) -> None:
        """Raise a clear syntax error with token location information."""
        if production is None:
            raise SyntaxError("Syntax error: unexpected end of input")

        column = self.lexer.find_column(production)
        raise SyntaxError(
            f"Syntax error: unexpected token {production.value!r} "
            f"at line {production.lineno}, column {column}"
        )

    def _validate_semantics(self, ast_root: ASTNode) -> None:
        """Run semantic validation, including control-flow blocks."""
        symbol_table = self.semantic_analyzer.symbol_table

        def validate_statement(node: ASTNode) -> None:
            if node.type == "Program" or node.type == "Block":
                for child in node.children:
                    validate_statement(child)
                return

            if node.type == "VarDecl":
                if node.children:
                    validate_expression(node.children[0])
                symbol_table.define(node.value, "int")
                return

            if node.type == "Assign":
                if symbol_table.lookup(node.value) is None:
                    raise SemanticError(f"Semantic Error: Variable '{node.value}' not declared")
                validate_expression(node.children[0])
                symbol_table.update(node.value, None)
                return

            if node.type == "Print":
                validate_expression(node.children[0])
                return

            if node.type == "Empty":
                return

            if node.type == "Goto" or node.type == "Label":
                return

            if node.type == "IF":
                validate_expression(node.children[0])
                validate_statement(node.children[1])
                return

            if node.type == "IF_ELSE":
                validate_expression(node.children[0])
                validate_statement(node.children[1])
                validate_statement(node.children[2])
                return

            if node.type == "WHILE":
                validate_expression(node.children[0])
                validate_statement(node.children[1])
                return

            if node.type == "FOR":
                init_node, condition_node, update_node, body_node = node.children
                if init_node.type != "Empty":
                    validate_statement(init_node)
                if condition_node.type != "Empty":
                    validate_expression(condition_node)
                validate_statement(body_node)
                if update_node.type != "Empty":
                    validate_statement(update_node)
                return

            raise SemanticError(f"Semantic Error: Unsupported statement type '{node.type}'")

        def validate_expression(node: ASTNode) -> None:
            if node.type == "Empty":
                return
            if node.type == "Number":
                return
            if node.type == "Identifier":
                if symbol_table.lookup(node.value) is None:
                    raise SemanticError(f"Semantic Error: Variable '{node.value}' not declared")
                return
            if node.type == "BinOp":
                validate_expression(node.children[0])
                validate_expression(node.children[1])
                return
            raise SemanticError(f"Semantic Error: Unsupported expression type '{node.type}'")

        validate_statement(ast_root)

    def _sanitize_ast(self, node: ASTNode | None) -> ASTNode:
        """Replace missing AST nodes with Empty nodes recursively."""
        if node is None:
            return ASTNode("Empty")

        sanitized_children = [self._sanitize_ast(child) for child in node.children]
        node.children = sanitized_children
        return node

    def _declaration_result(self, declarations: list[ASTNode]) -> ASTNode:
        """Return a single declaration or a Block for comma declarations."""
        if len(declarations) == 1:
            return declarations[0]
        return ASTNode("Block", children=declarations)


if __name__ == "__main__":
    sample_code = """
    for (;;) {
        print(1);
    }
    """

    parser = CompilerParser()
    ast_root = parser.parse(sample_code)
    print(ast_root.to_dict())
