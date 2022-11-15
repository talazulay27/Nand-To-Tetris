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
TEMP_BASE_CELL = 5
LOAD_BIGGEST_CELL = "@32767\n"

calls_and_returns_counter = 0
labels_counter = 0


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.out = output_stream
        self.memories = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
        self.file_name = ""

    def write_init(self):

        # SP = 256
        self.out.write("// Initialization \n")
        self.out.write("@256\n")
        self.out.write("D=A\n")
        self.out.write("@SP\n")
        self.out.write("M = D\n")

        # Call Sys.init
        self.out.write("// Call Sys.init\n")
        self.write_call("Sys.init", 0)

    def write_label(self, label: str):
        self.out.write("// Write label: " + label + "\n")
        self.out.write("(" + label + ")\n")

    def write_goto(self, label: str):
        self.out.write("// Go to " + label + "\n")
        self.out.write("@" + label + "\n")
        self.out.write("0;JMP\n")

    def write_if(self, label: str):
        self.out.write("// Go to if " + label + "\n")
        self.out.write("@SP\n")
        self.out.write("M = M-1\n")
        self.out.write("A = M\n")
        self.out.write("D = M\n")
        self.out.write("@" + label + "\n")
        self.out.write("D;JNE\n")

    def write_call(self, function_name: str, num_args: int):

        global calls_and_returns_counter
        self.out.write("// Call " + function_name + " " + str(num_args) + "\n")

        # Create and PUSH return address label

        self.out.write(
            "@" + function_name + ".returnAddress" + str(calls_and_returns_counter) + "\n")
        self.out.write("D = A\n")
        self.out.write("@SP\n")
        self.out.write("A=M\n")
        self.out.write("M=D\n")
        self.out.write("@SP\n")
        self.out.write("M = M+1\n")

        # Push LCL, ARG, THIS and THAT

        for memory in self.memories.values():
            self.out.write("@" + memory + "\n")
            self.out.write("D=M\n")  # Change from A to M
            self.out.write("@SP\n")
            self.out.write("A=M\n")
            self.out.write("M=D\n")
            self.out.write("@SP\n")
            self.out.write("M = M+1\n")

        # ARG = SP-nArgs-5
        self.out.write("@" + str(num_args + 5) + "\n")
        self.out.write("D=A\n")  # D = number of args
        self.out.write("@SP\n")
        self.out.write("D = M - D\n")
        self.out.write("@ARG\n")
        self.out.write("M=D\n")

        # LCL = SP
        self.out.write("@SP\n")
        self.out.write("D = M\n")
        self.out.write("@LCL\n")
        self.out.write("M = D\n")

        # goto function

        self.write_goto(function_name)
        self.write_label(function_name + ".returnAddress" + str(calls_and_returns_counter))
        calls_and_returns_counter += 1

    def write_return(self):

        self.out.write("// Return \n")
        # frame = LCL
        self.out.write("@LCL\n")
        self.out.write("D = M\n")
        self.out.write("@endFrame\n")
        self.out.write("M = D\n")

        # retAddr = *(endFrame-5)

        self.out.write("@5\n")
        self.out.write("D = A\n")
        self.out.write("@endFrame\n")
        self.out.write("A = M - D\n")
        self.out.write("D = M\n")
        self.out.write("@retAddr\n")
        self.out.write("M = D\n")

        # *ARG = pop
        self.out.write("@SP\n")
        self.out.write("AM = M -1\n")
        self.out.write("D = M\n")
        self.out.write("@ARG\n")
        self.out.write("A = M\n")
        self.out.write("M =D\n")

        # SP = ARG+1
        self.out.write("@ARG\n")
        self.out.write("D = M +1\n")
        self.out.write("@SP\n")
        self.out.write("M = D\n")

        index = 4
        for memory in self.memories.values():
            self.out.write("@" + str(index) + "\n")
            self.out.write("D = A\n")
            self.out.write("@endFrame\n")
            self.out.write("A = M - D\n")
            self.out.write("D = M\n")
            self.out.write("@" + memory + "\n")
            self.out.write("M = D\n")
            index -=1

        self.out.write("@retAddr\n")
        self.out.write("A = M\n")
        self.out.write("0;JMP\n")

    def write_function(self, function_name: str, num_locals: int):
        self.out.write("// Function " + function_name + " " + str(num_locals) + "\n")
        self.write_label(function_name)
        for i in range(num_locals):
            self.write_push_pop(C_PUSH, "constant", 0)

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """

        global labels_counter

        self.out.write("// " + command + "\n")
        if command == "add" or command == "sub" or command == "and" or command == "or":
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M\n")
            self.out.write("D = M\n")
            self.out.write("A = A-1\n")
            if command == "sub":
                self.out.write("M = M-D\n")
            elif command == "add":
                self.out.write("M = D+M\n")
            elif command == "and":
                self.out.write("M = M&D\n")
            else:
                self.out.write("M = M|D\n")

        if command == "neg" or command == "not" or command == "shiftleft" or command == "shiftright":
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M\n")
            if command == "neg":
                self.out.write("M = -M\n")
            elif command == "not":
                self.out.write("M = !M\n")
            elif command == "shiftleft":
                self.out.write("M<<\n")
            else:
                self.out.write("M>>\n")

            self.out.write("@SP\n")
            self.out.write("M = M+1\n")

        if command == "eq" or command == "gt" or command == "lt":
            if command == "eq":
                label = "JEQ"
            elif command == "gt":
                label = "JGT"
            else:
                label = "JLT"

            # Checks if the numbers have same sign

            self.out.write(LOAD_BIGGEST_CELL)
            self.out.write("D=!A\n")
            self.out.write("@SP\n")
            self.out.write("A = M-1\n")
            self.out.write("D=D&M\n")
            self.out.write("@R13\n")
            self.out.write("M=D\n")

            self.out.write(LOAD_BIGGEST_CELL)
            self.out.write("D=!A\n")
            self.out.write("@SP\n")
            self.out.write("A = M-1\n")
            self.out.write("A = A - 1\n")
            self.out.write("D=D&M\n")
            self.out.write("@R14\n")
            self.out.write("M=D\n")

            # Case: same sign

            self.out.write("@R13\n")
            self.out.write("D = M\n")
            self.out.write("@R14\n")
            self.out.write("D = M-D\n")
            self.out.write("@SAME_SIGN" + str(labels_counter) + "\n")
            self.out.write("D;JEQ\n")

            # Case: different sign

            self.out.write("@R14\n")
            self.out.write("D = M\n")

            if command == "gt":
                self.out.write("@PUT_TRUE" + str(labels_counter) + "\n")
                self.out.write("D;JEQ\n")
            elif command == "lt":
                self.out.write("@PUT_TRUE" + str(labels_counter) + "\n")
                self.out.write("D;JLT\n")

            # Case: different sign and FALSE
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M-1\n")
            self.out.write("M = 0\n")
            self.out.write("@END" + str(labels_counter) + "\n")
            self.out.write("0;JMP\n")

            # Case: same sign

            self.out.write("(SAME_SIGN" + str(labels_counter) + ")\n")
            self.out.write("@SP\n")
            self.out.write("A = M-1\n")
            self.out.write("D = M\n")
            self.out.write("@R13\n")
            self.out.write("M = D\n")
            self.out.write("@SP\n")
            self.out.write("A = M - 1 \n")
            self.out.write("A = A - 1 \n")
            self.out.write("D = M\n")
            self.out.write("@R14\n")
            self.out.write("M = D\n")
            self.out.write("@R13\n")
            self.out.write("D = M\n")
            self.out.write("@R14\n")
            self.out.write("D = M-D\n")
            self.out.write("@PUT_TRUE" + str(labels_counter) + "\n")
            self.out.write("D;" + label + "\n")
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M-1\n")
            self.out.write("M = 0\n")
            self.out.write("@END" + str(labels_counter) + "\n")
            self.out.write("0;JMP\n")
            self.out.write("(PUT_TRUE" + str(labels_counter) + ")\n")
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M-1\n")
            self.out.write("M = -1\n")
            self.out.write("(END" + str(labels_counter) + ")\n")
            labels_counter += 1

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """

        self.out.write("// " + command + " " + segment + " " + str(index) + "\n")

        if segment in self.memories:

            cell = self.memories[segment]

            if command == C_PUSH:
                self.out.write("@" + str(cell) + "\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("A=D\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A = M\n")
                self.out.write("M = D\n")
                self.out.write("@SP\n")
                self.out.write("M = M+1" + "\n")

            elif command == C_POP:

                self.out.write("@" + str(cell) + "\n")
                self.out.write("D=M\n")
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=D+A\n")
                self.out.write("@R13\n")
                self.out.write("M = D\n")
                self.out.write("@SP\n")
                self.out.write("M = M-1\n")
                self.out.write("A = M\n")
                self.out.write("D = M\n")
                self.out.write("@R13\n")
                self.out.write("A = M\n")
                self.out.write("M = D\n")

        elif segment == "constant":

            if command == C_PUSH:
                self.out.write("@" + str(index) + "\n")
                self.out.write("D=A\n")
                self.out.write("@SP\n")
                self.out.write("A = M\n")
                self.out.write("M = D\n")
                self.out.write("@SP\n")
                self.out.write("M = M+1" + "\n")

        elif segment == "static" or segment == "temp" or segment == "pointer":

            if segment == "static":
                cell = "static." + self.file_name + str(index)
            elif segment == "temp":
                cell = str(TEMP_BASE_CELL + index)
            else:  # pointer

                if index:
                    cell = "THAT"
                else:
                    cell = "THIS"

            if command == C_PUSH:
                self.out.write("@" + cell + "\n")
                self.out.write("D=M\n")
                self.out.write("@SP\n")
                self.out.write("A = M\n")
                self.out.write("M = D\n")
                self.out.write("@SP\n")
                self.out.write("M = M+1" + "\n")

            elif command == C_POP:

                self.out.write("@SP\n")
                self.out.write("M = M-1\n")
                self.out.write("A = M\n")
                self.out.write("D = M\n")
                self.out.write("@" + str(cell) + "\n")
                self.out.write("M = D\n")

    def close(self) -> None:
        """Closes the output file."""
        self.out.close()
