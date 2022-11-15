"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import math

from JackTokenizer import *
from VMWriter import *
from SymbolTable import *

CONSTANT = "constant"
TEMP = "temp"
MEM_ALLOC = "Memory.alloc"
STRING_ALLOC = "String.new"
APPEND_CHAR = "String.appendChar"


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
        self.vm_writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.if_label_counter = 0
        self.while_label_counter = 0
        self.var_counter = 0
        self.class_name = ''

    def compile_class(self) -> None:
        """Compiles a complete class."""
        self.jack.advance()
        self.class_name = self.jack.current_token
        self.jack.advance()
        while self.jack.has_more_tokens():
            if self.jack.current_token == "field" or self.jack.current_token == "static":
                self.compile_class_var_dec()
            elif self.jack.current_token == "function" or self.jack.current_token == "method" or self.jack.current_token == "constructor":
                self.compile_subroutine()
            else:
                self.jack.advance()

        self.jack.advance()

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        var_kind = self.jack.current_token
        self.jack.advance()
        var_type = self.jack.current_token
        self.jack.advance()
        while self.jack.current_token != ";":
            if self.jack.current_token == ',':
                self.jack.advance()
            self.symbol_table.define(self.jack.current_token, var_type, var_kind)
            self.jack.advance()

        self.jack.advance()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        subroutine_type = self.jack.current_token
        self.jack.advance()
        self.jack.advance()
        subroutine_name = self.class_name + '.' + self.jack.current_token
        self.jack.advance()
        self.symbol_table.start_subroutine()
        if subroutine_type == "method":
            self.symbol_table.define("this", self.class_name, ARG)
        self.compile_parameter_list()
        self.var_counter = 0
        self.jack.advance()
        while self.jack.current_token == "var":
            self.compile_var_dec()
        self.vm_writer.write_function(subroutine_name, self.var_counter)
        if subroutine_type == "constructor":
            self.vm_writer.write_push(CONSTANT, self.symbol_table.var_count(FIELD))
            self.vm_writer.write_call(MEM_ALLOC, 1)
            self.vm_writer.write_pop(POINTER, 0)
        elif subroutine_type == "method":
            self.vm_writer.write_push(ARG, 0)
            self.vm_writer.write_pop(POINTER, 0)

        self.compile_subroutine_body()

    def compile_subroutine_body(self):
        while self.jack.current_token != "}":
            self.compile_statements()
        self.jack.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        self.jack.advance()
        while self.jack.current_token != ")":
            if self.jack.current_token == ',':
                self.jack.advance()
            arg_type = self.jack.current_token
            self.jack.advance()
            arg_name = self.jack.current_token
            self.symbol_table.define(arg_name, arg_type, ARG)
            self.jack.advance()
        self.jack.advance()

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""

        self.jack.advance()
        var_type = self.jack.current_token
        self.jack.advance()
        while self.jack.current_token != ";":
            self.symbol_table.define(self.jack.current_token, var_type, VAR)
            self.var_counter += 1
            self.jack.advance()
            if self.jack.current_token == ',':
                self.jack.advance()
        self.jack.advance()

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing
        "{}".
        """
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
                self.jack.advance()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        self.jack.advance()
        self.subroutine_call()
        self.jack.advance()
        self.vm_writer.write_pop(TEMP, 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""

        self.jack.advance()  # remove let
        segment = self.symbol_table.kind_of(self.jack.current_token)
        position = self.symbol_table.index_of(self.jack.current_token)
        if self.jack.get_next_token() == '[':
            self.jack.advance()
            self.jack.advance()
            self.compile_expression()
            self.jack.advance()  # remove ]
            self.vm_writer.write_push(segment, position)  # array address in heap
            self.vm_writer.write_arithmetic('+')
            # self.vm_writer.write_pop(POINTER, 1)  # saves address of the index in the array
            self.jack.advance()  # remove '='
            self.compile_expression()
            self.vm_writer.write_pop(TEMP,0)
            self.vm_writer.write_pop(POINTER, 1)
            self.vm_writer.write_push(TEMP, 0)
            self.vm_writer.write_pop("that", 0)
        else:
            self.jack.advance()
            self.jack.advance()  # remove '='
            self.compile_expression()
            self.vm_writer.write_pop(segment, position)

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.jack.advance()  # remove while
        while_label = "WHILE" + str(self.while_label_counter)
        out_while_label = "WHILE_END" + str(self.while_label_counter)
        self.while_label_counter += 1
        self.vm_writer.write_label(while_label)
        self.compile_expression()
        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(out_while_label)
        self.compile_statements()
        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(out_while_label)
        self.jack.advance()

    def compile_return(self) -> None:
        """Compiles a return statement."""

        if self.jack.get_next_token() != ';':
            self.jack.advance()
            self.compile_expression()
        else:
            self.vm_writer.write_push(CONSTANT, 0)
        self.vm_writer.write_return()
        self.jack.advance()

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        if_label = "IF_TRUE" + str(self.if_label_counter)
        else_label = "IF_FALSE" + str(self.if_label_counter)
        end_label = "IF_END" + str(self.if_label_counter)
        self.if_label_counter += 1
        self.jack.advance()  # remove if
        self.compile_expression()
        # self.vm_writer.write_arithmetic("neg")
        self.vm_writer.write_if(if_label)
        self.vm_writer.write_goto(else_label)
        self.vm_writer.write_label(if_label)
        self.compile_statements()
        self.jack.advance()
        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(else_label)
        if self.jack.current_token == "else":
            self.compile_statements()
            self.jack.advance()
        self.vm_writer.write_label(end_label)

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.compile_term()
        self.jack.advance()
        while self.jack.current_token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op = self.jack.current_token
            self.jack.advance()
            self.compile_term()
            self.jack.advance()
            self.vm_writer.write_arithmetic(op)

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

        if self.jack.token_type() == INT_CONST:
            self.vm_writer.write_push(CONSTANT, self.jack.current_token)
        elif self.jack.token_type() == STRING_CONST:
            string = self.jack.current_token[1:-1]
            self.vm_writer.write_push(CONSTANT, len(string))
            self.vm_writer.write_call(STRING_ALLOC, 1)
            for i in range(len(string)):
                self.vm_writer.write_push(CONSTANT, ord(string[i]))
                self.vm_writer.write_call(APPEND_CHAR, 2)
        elif self.jack.current_token == '(':
            self.jack.advance()
            self.compile_expression()
        elif self.jack.current_token == "this":
            self.vm_writer.write_push(POINTER, 0)
        elif self.jack.current_token == "true":
            self.vm_writer.write_push(CONSTANT, 0)
            self.vm_writer.write_arithmetic("not")
        elif self.jack.current_token in ["false", 'null']:
            self.vm_writer.write_push(CONSTANT, 0)
        elif self.jack.current_token in ['-', '~', '^', "#"]:
            op = self.jack.special_symbols[self.jack.current_token]
            self.jack.advance()
            self.compile_term()
            self.vm_writer.write_arithmetic(op)
        elif self.jack.token_type() == IDENTIFIER:
            if self.jack.get_next_token() == '(' or self.jack.get_next_token() == '.':
                self.subroutine_call()
            elif self.jack.get_next_token() == '[':
                identifier = self.jack.current_token
                self.jack.advance()
                self.jack.advance()
                self.compile_expression()
                segment = self.symbol_table.kind_of(identifier)
                position = self.symbol_table.index_of(identifier)
                self.vm_writer.write_push(segment, position)
                self.vm_writer.write_arithmetic('+')
                self.vm_writer.write_pop(POINTER, 1)
                self.vm_writer.write_push("that", 0)
            else:
                segment = self.symbol_table.kind_of(self.jack.current_token)
                position = self.symbol_table.index_of(self.jack.current_token)
                self.vm_writer.write_push(segment, position)

    def subroutine_call(self):
        method = False
        function_name = ''
        # saving the name of the subroutine
        while self.jack.current_token != '(':
            function_name += self.jack.current_token
            self.jack.advance()
        args_counter = 0
        if '.' not in function_name:
            method = True
            function_name = self.class_name + '.' + function_name
        else:
            if self.symbol_table.type_of(function_name.split('.')[0]) != ERR:
                segment = self.symbol_table.kind_of(function_name.split('.')[0])
                position = self.symbol_table.index_of(function_name.split('.')[0])
                function_name = self.symbol_table.type_of(function_name.split('.')[0]) + '.' + function_name.split('.')[
                    1]
                self.vm_writer.write_push(segment, position)
                args_counter = 1
        self.jack.advance()
        if method:
            self.vm_writer.write_push(POINTER, 0)
            args_counter = 1
        while self.jack.current_token != ')':
            self.compile_expression()
            args_counter += 1
            if self.jack.current_token == ",":
                self.jack.advance()  ##check for double advance
        self.vm_writer.write_call(function_name, args_counter)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""

        while self.jack.current_token != ")":
            if self.jack.current_token == ",":
                self.jack.advance()
            else:
                self.compile_expression()
