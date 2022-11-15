"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

C_ARITHMETIC = "C_ARITHMETIC"
C_PUSH = "C_PUSH"
C_GOTO = "C_GOTO"
C_POP = "C_POP"
C_LABEL = "C_LABEL"
C_IF = "C_IF"
C_FUNCTION = "C_FUNCTION"
C_RETURN = "C_RETURN"
C_CALL = "C_CALL"




class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """


    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.arithmetic_commands = ["add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not", "shiftleft", "shiftright"]
        input_lines = input_file.read().splitlines()
        lines_with_no_comments = [line.split("//")[0] for line in input_lines if line and line[0] != "/"]
        lines_with_no_comments_and_tabs = [line.split("\t")[0] for line in lines_with_no_comments]
        self.commands = [line.split(' ') for line in lines_with_no_comments_and_tabs]
        self.total_commands = len(self.commands)
        self.command_counter = 0
        self.current_command = self.commands[self.command_counter]

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.command_counter < self.total_commands

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.command_counter += 1
        if self.has_more_commands():
            self.current_command = self.commands[self.command_counter]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.current_command[0] in self.arithmetic_commands:
            return C_ARITHMETIC
        elif self.current_command[0] == "push":
            return C_PUSH
        elif self.current_command[0] == "pop":
            return C_POP
        elif self.current_command[0] == "call":
            return C_CALL
        elif self.current_command[0] == "function":
            return C_FUNCTION
        elif self.current_command[0] == "return":
            return C_RETURN
        elif self.current_command[0] == "label":
            return C_LABEL
        elif self.current_command[0] == "if-goto":
            return C_IF
        elif self.current_command[0] == "goto":
            return C_GOTO

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        if self.command_type() == C_ARITHMETIC:
            return self.current_command[0]
        elif self.command_type() != C_RETURN:
            return self.current_command[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.current_command[2])
