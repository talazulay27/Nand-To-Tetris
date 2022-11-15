"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

A_COMMAND = "A_COMMAND"
C_COMMAND = "C_COMMAND"
L_COMMAND = "L_COMMAND"
A_COUNTER = 16


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """

    symbol_table = SymbolTable()
    parser = Parser(input_file)
    code = Code
    current_code_line = ""
    no_l_commands_counter = 0
    while parser.has_more_commands():
        if parser.command_type() == L_COMMAND:
            symbol_table.add_entry(parser.symbol(), no_l_commands_counter)
        else:
            no_l_commands_counter += 1
        parser.advance()

    parser.command_counter = 0
    parser.current_command = parser.commands[0]

    a_command_counter = A_COUNTER
    while parser.has_more_commands():
        if parser.command_type() == A_COMMAND:
            if not parser.symbol().isnumeric() and not symbol_table.contains(parser.symbol()):
                symbol_table.add_entry(parser.symbol(), a_command_counter)
                a_command_counter += 1
        parser.advance()
    parser.command_counter = 0
    parser.current_command = parser.commands[0]

    while parser.has_more_commands():
        if parser.command_type() == C_COMMAND:
            current_code_line += "111"
            current_code_line += code.comp(parser.comp())
            current_code_line += code.dest(parser.dest())
            current_code_line += code.jump(parser.jump())
        elif parser.command_type() == A_COMMAND:
            if symbol_table.contains(parser.symbol()):
                current_code_line = bin(symbol_table.symbol_table[parser.symbol()])[2:].zfill(16)
            else:
                current_code_line = bin(int(parser.symbol()))[2:].zfill(16)
        else:
            parser.advance()
            current_code_line = ""
            continue

        output_file.write(current_code_line + '\n')
        parser.advance()
        current_code_line = ""


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
