"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import *

OPEN_CLASS_DECLARATION = "<class>\n"
CLOSE_CLASS_DECLARATION = "</class>\n"
PATTERN_DECLARATION = "<type> name </type>\n"
OPEN_LET_DECLARATION = "<letStatement>\n"
CLOSE_LET_DECLARATION = "</letStatement>\n"
OPEN_WHILE_DECLARATION = "<whileStatement>\n"
CLOSE_WHILE_DECLARATION = "</whileStatement>\n"
OPEN_IF_DECLARATION = "<ifStatement>\n"
CLOSE_IF_DECLARATION = "</ifStatement>\n"
OPEN_RETURN_DECLARATION = "<returnStatement>\n"
CLOSE_RETURN_DECLARATION = "</returnStatement>\n"
OPEN_DO_DECLARATION = "<doStatement>\n"
CLOSE_DO_DECLARATION = "</doStatement>\n"
OPEN_STATEMENTS_DECLARATION = "<statements>\n"
CLOSE_STATEMENTS_DECLARATION = "</statements>\n"
OPEN_CLASS_VAR_DECLARATION = "<classVarDec>\n"
CLOSE_CLASS_VAR_DECLARATION = "</classVarDec>\n"
OPEN_SUBROUTINE_DEC = "<subroutineDec>\n"
CLOSE_SUBROUTINE_DEC = "</subroutineDec>\n"
OPEN_SUBROUTINE_BODY = "<subroutineBody>\n"
CLOSE_SUBROUTINE_BODY = "</subroutineBody>\n"
OPEN_PARAMETERS_LIST = "<parameterList>\n"
CLOSE_PARAMETERS_LIST = "</parameterList>\n"
OPEN_VAR_DEC = "<varDec>\n"
CLOSE_VAR_DEC = "</varDec>\n"
OPEN_EXPRESSION_LIST = "<expressionList>\n"
CLOSE_EXPRESSION_LIST = "</expressionList>\n"
OPEN_EXPRESSION_DEC = "<expression>\n"
CLOSE_EXPRESSION_DEC = "</expression>\n"
OPEN_TERM_DEC = "<term>\n"
CLOSE_TERM_DEC = "</term>\n"


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.terminal_rules = [INT_CONST, STRING_CONST, KEYWORD, SYMBOL]
        self.jack = JackTokenizer(input_stream)
        self.output_file = output_stream

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.output_file.write(OPEN_CLASS_DECLARATION)
        while self.jack.has_more_tokens():
            if self.jack.current_token in ["return", "do", "let", "if", "while"]:
                self.compile_statements()
            elif self.jack.current_token == "function" or self.jack.current_token == "method" or self.jack.current_token == "constructor":
                self.compile_subroutine()
            elif self.jack.current_token == "field" or self.jack.current_token == "static":
                self.compile_class_var_dec()
            else:
                self.write_and_advance()

        self.output_file.write(CLOSE_CLASS_DECLARATION)

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_file.write(OPEN_CLASS_VAR_DECLARATION)
        while self.jack.current_token != ";":
            self.write_and_advance()
        self.write_and_advance()
        self.output_file.write(CLOSE_CLASS_VAR_DECLARATION)

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        self.output_file.write(OPEN_SUBROUTINE_DEC)
        while self.jack.current_token != '(':
            self.write_and_advance()
        self.write_and_advance()
        self.compile_parameter_list()
        self.write_and_advance()
        self.compile_subroutine_body()

        self.output_file.write(CLOSE_SUBROUTINE_DEC)

    def compile_subroutine_body(self):
        self.output_file.write(OPEN_SUBROUTINE_BODY)
        self.write_and_advance()
        while self.jack.current_token != "}":
            if self.jack.current_token == "var":
                self.compile_var_dec()
            else:
                self.compile_statements()
        self.write_and_advance()
        self.output_file.write(CLOSE_SUBROUTINE_BODY)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.output_file.write(OPEN_PARAMETERS_LIST)
        while self.jack.current_token != ")":
            self.write_and_advance()

        self.output_file.write(CLOSE_PARAMETERS_LIST)

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        self.output_file.write(OPEN_VAR_DEC)
        while self.jack.current_token != ';':
            self.write_and_advance()
        self.write_and_advance()
        self.output_file.write(CLOSE_VAR_DEC)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
        self.output_file.write(OPEN_STATEMENTS_DECLARATION)
        while self.jack.current_token != "}":
            if self.jack.current_token == "let":
                self.compile_let()

            elif self.jack.current_token == "while":
                self.compile_while()

            elif self.jack.current_token == "if":
                self.compile_if()

            elif self.jack.current_token == "return":
                self.compile_return()

            elif self.jack.current_token == "do":
                self.compile_do()

            else:
                self.write_and_advance()

        self.output_file.write(CLOSE_STATEMENTS_DECLARATION)

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.output_file.write(OPEN_DO_DECLARATION)
        self.write_and_advance()
        self.subroutine_call()
        self.write_and_advance()
        self.write_and_advance()
        self.output_file.write(CLOSE_DO_DECLARATION)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_file.write(OPEN_LET_DECLARATION)
        self.write_and_advance()
        self.write_and_advance()
        if self.jack.current_token == "[":
            self.write_and_advance()
            self.compile_expression()
            self.write_and_advance()
        self.write_and_advance()
        self.compile_expression()
        self.write_and_advance()
        self.output_file.write(CLOSE_LET_DECLARATION)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_file.write(OPEN_WHILE_DECLARATION)
        self.write_and_advance()
        self.write_and_advance()
        self.compile_expression()
        self.write_and_advance()
        self.write_and_advance()
        self.compile_statements()
        self.write_and_advance()
        self.output_file.write(CLOSE_WHILE_DECLARATION)

    def write_and_advance(self):

        type = self.jack.token_type()
        if self.jack.token_type() == STRING_CONST:
            name = self.jack.current_token[1:-1]
        elif self.jack.current_token in self.jack.special_symbols:
            name = self.jack.special_symbols[self.jack.current_token]
        else:
            name = self.jack.current_token
        self.output_file.write(PATTERN_DECLARATION.replace("type", type).replace("name", name))
        self.jack.advance()

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_file.write(OPEN_RETURN_DECLARATION)
        self.write_and_advance()
        if self.jack.current_token != ';':
            self.compile_expression()
        self.write_and_advance()
        self.output_file.write(CLOSE_RETURN_DECLARATION)

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        self.output_file.write(OPEN_IF_DECLARATION)
        self.write_and_advance()
        self.write_and_advance()
        self.compile_expression()
        self.write_and_advance()
        self.write_and_advance()
        self.compile_statements()
        self.write_and_advance()

        if self.jack.current_token == "else":
            self.write_and_advance()
            self.write_and_advance()
            self.compile_statements()
            self.write_and_advance()

        self.output_file.write(CLOSE_IF_DECLARATION)

    def compile_expression(self) -> None:
        """Compiles an expression."""

        self.output_file.write(OPEN_EXPRESSION_DEC)
        self.compile_term()
        while self.jack.current_token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.write_and_advance()
            self.compile_term()
        self.output_file.write(CLOSE_EXPRESSION_DEC)

    def compile_term(self) -> None:
        """Compiles a term.
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        self.output_file.write(OPEN_TERM_DEC)
        if self.jack.token_type() == IDENTIFIER:
            if self.jack.get_next_token() == '(' or self.jack.get_next_token() == '.':
                self.write_and_advance()
                self.subroutine_call()
                self.write_and_advance()
            elif self.jack.get_next_token() == '[':
                self.write_and_advance()
                self.write_and_advance()
                self.compile_expression()
                self.write_and_advance()
            else:
                self.write_and_advance()
        elif self.jack.current_token in ['-', '~', '^', "#"]:
            self.write_and_advance()
            self.compile_term()
        elif self.jack.current_token == "(":
            self.write_and_advance()
            self.compile_expression()
            self.write_and_advance()
        else:
            self.write_and_advance()
        self.output_file.write(CLOSE_TERM_DEC)

    def subroutine_call(self):
        if self.jack.current_token == '(':
            self.write_and_advance()
            self.compile_expression_list()
        else:
            while self.jack.current_token != '(':
                self.write_and_advance()
            self.write_and_advance()
            self.compile_expression_list()

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        self.output_file.write(OPEN_EXPRESSION_LIST)
        while self.jack.current_token != ")":
            if self.jack.current_token == ",":
                self.write_and_advance()
            else:
                self.compile_expression()
        self.output_file.write(CLOSE_EXPRESSION_LIST)
