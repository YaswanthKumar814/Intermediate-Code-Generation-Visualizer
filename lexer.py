"""PLY-based lexical analyzer for the Intermediate Code Generation Visualizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List
import sys

import ply.lex as lex


@dataclass(slots=True)
class Token:
    """Represents a lexical token produced from the input source code."""

    token_type: str
    value: Any
    line: int
    column: int


RESERVED_KEYWORDS = {
    "int": "INT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "print": "PRINT",
}

PLY_TOKENS = (
    "IDENTIFIER",
    "NUMBER",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "ASSIGN",
    "SEMICOLON",
    "LPAREN",
    "RPAREN",
    "LBRACE",
    "RBRACE",
) + tuple(RESERVED_KEYWORDS.values())

tokens = PLY_TOKENS

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_ASSIGN = r"="
t_SEMICOLON = r";"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_ignore = " \t\r"


def t_COMMENT_SINGLE(token):
    r"//[^\n]*"
    # Ignore single-line comments.


def t_COMMENT_MULTI(token):
    r"/\*[\s\S]*?\*/"
    # Ignore multi-line comments while preserving line numbers.
    token.lexer.lineno += token.value.count("\n")


def _find_column(lexdata: str, lexpos: int) -> int:
    """Compute the 1-based column for a token position."""
    line_start = lexdata.rfind("\n", 0, lexpos) + 1
    return lexpos - line_start + 1


def t_IDENTIFIER(token):
    r"[A-Za-z_][A-Za-z0-9_]*"
    # Match identifiers and convert reserved words to keyword tokens.
    token.type = RESERVED_KEYWORDS.get(token.value, "IDENTIFIER")
    return token


def t_NUMBER(token):
    r"\d+"
    # Match integer literals.
    token.value = int(token.value)
    return token


def t_newline(token):
    r"\n+"
    # Track line numbers when newline characters are encountered.
    token.lexer.lineno += len(token.value)


def t_error(token):
    """Raise a clear lexical error for illegal characters."""
    column = _find_column(token.lexer.lexdata, token.lexpos)
    character = token.value[0]
    raise SyntaxError(
        f"Lexical error: invalid character {character!r} at line {token.lineno}, column {column}"
    )


class CompilerLexer:
    """Thin wrapper around the PLY lexer used by the rest of the project."""

    reserved = RESERVED_KEYWORDS
    tokens = PLY_TOKENS

    def __init__(self) -> None:
        """Build the underlying PLY lexer instance."""
        self.lexer = lex.lex(module=sys.modules[__name__], debug=False)

    def find_column(self, token) -> int:
        """Compute the 1-based column position for a PLY token."""
        return _find_column(self.lexer.lexdata, token.lexpos)

    def tokenize(self, source_code: str) -> List[Token]:
        """Convert source code text into a list of Token objects."""
        self.lexer.lineno = 1
        self.lexer.input(source_code)

        output_tokens: List[Token] = []
        while True:
            ply_token = self.lexer.token()
            if ply_token is None:
                break
            output_tokens.append(
                Token(
                    token_type=ply_token.type,
                    value=ply_token.value,
                    line=ply_token.lineno,
                    column=self.find_column(ply_token),
                )
            )
        return output_tokens


def tokenize(input_code: str) -> List[Token]:
    """Tokenize the provided source code using a fresh lexer instance."""
    return CompilerLexer().tokenize(input_code)


if __name__ == "__main__":
    sample_code = """
    // single-line comment
    int a = 5;
    /* multi-line
       comment */
    print(a);
    """

    print("Input:")
    print(sample_code.strip())
    print("\nTokens:")
    for token in tokenize(sample_code):
        print(token)
