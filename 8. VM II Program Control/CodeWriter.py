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


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    current_function_name = "Sys.init"
    frames_counter = 0
    labels_counter = 0
    returns_counter = 0

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
        self.write_call("Sys.init", 0)

    def write_label(self, label: str):
        self.out.write("// Write label: " + CodeWriter.current_function_name + "$" + label + "\n")
        self.out.write("(" + CodeWriter.current_function_name + "$" + label + ")\n")

    def write_goto(self, label: str):
        self.out.write("// Go to " + CodeWriter.current_function_name + "$" + label + "\n")
        self.out.write("@" + CodeWriter.current_function_name + "$" + label + "\n")
        self.out.write("0;JMP\n")

    def write_if(self, label: str):
        self.out.write("// Go to if " + CodeWriter.current_function_name + "$" + label + "\n")
        self.out.write("@SP\n")
        self.out.write("M = M-1\n")
        self.out.write("A = M\n")
        self.out.write("D = M\n")
        self.out.write("@" + CodeWriter.current_function_name + "$" + label + "\n")
        self.out.write("D;JNE\n")

    def write_call(self, function_name: str, num_args: int):

        self.out.write("// Call " + function_name + " " + str(num_args) + "\n")

        return_label = "ret." + str(CodeWriter.returns_counter)
        CodeWriter.returns_counter += 1

        # Create and PUSH return address label
        self.out.write("@" + self.current_function_name + "$" + return_label + "\n")
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

        self.out.write("@" + function_name + "\n")
        self.out.write("0;JMP\n")
        self.write_label(return_label)

    def write_return(self):

        end_frame = "@endFrame" + str(CodeWriter.frames_counter) + "\n"
        ret_addr = "@retAddr" + str(CodeWriter.frames_counter) + "\n"
        CodeWriter.frames_counter += 1

        self.out.write("// Return \n")
        # frame = LCL
        self.out.write("@LCL\n")
        self.out.write("D = M\n")
        self.out.write(end_frame)
        self.out.write("M = D\n")

        # retAddr = *(endFrame-5)

        self.out.write("@5\n")
        self.out.write("D = A\n")
        self.out.write(end_frame)
        self.out.write("A = M - D\n")
        self.out.write("D = M\n")
        self.out.write(ret_addr)
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
            self.out.write(end_frame)
            self.out.write("A = M - D\n")
            self.out.write("D = M\n")
            self.out.write("@" + memory + "\n")
            self.out.write("M = D\n")
            index -= 1

        self.out.write(ret_addr)
        self.out.write("A = M\n")
        self.out.write("0;JMP\n")

    def write_function(self, function_name: str, num_locals: int):
        CodeWriter.current_function_name = function_name

        self.out.write("// Function " + function_name + " " + str(num_locals) + "\n")
        self.out.write("(" + function_name + ")\n")
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

        if command == "neg" or command == "not" or command == "shiftleft" or\
                command == "shiftright":
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M\n")
            if command == "neg":
                self.out.write("M = -M\n")
            elif command == "not":
                self.out.write("M = !M\n")
            elif command == "shiftleft":
                self.out.write("M = M<<\n")
            else:
                self.out.write("M = M>>\n")

            self.out.write("@SP\n")
            self.out.write("M = M+1\n")

        if command == "eq" or command == "gt" or command == "lt":

            current_label_counter_value = CodeWriter.labels_counter
            CodeWriter.labels_counter += 1

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
            self.out.write("@" + self.current_function_name + "$SAME_SIGN" +
                           str(current_label_counter_value) + "\n")
            self.out.write("D;JEQ\n")

            # Case: different sign

            self.out.write("@R14\n")
            self.out.write("D = M\n")

            if command == "gt":
                self.out.write("@" + self.current_function_name + "$PUT_TRUE" +
                               str(current_label_counter_value) + "\n")
                self.out.write("D;JEQ\n")
            elif command == "lt":
                self.out.write("@" + self.current_function_name + "$PUT_TRUE" +
                               str(current_label_counter_value) + "\n")
                self.out.write("D;JLT\n")

            # Case: different sign and FALSE
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M-1\n")
            self.out.write("M = 0\n")
            self.out.write("@" + self.current_function_name + "$END" +
                           str(current_label_counter_value) + "\n")
            self.out.write("0;JMP\n")

            # Case: same sign

            self.write_label("SAME_SIGN" + str(current_label_counter_value))
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
            self.out.write("@" + self.current_function_name + "$PUT_TRUE" +
                           str(current_label_counter_value) + "\n")
            self.out.write("D;" + label + "\n")
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M-1\n")
            self.out.write("M = 0\n")
            self.out.write("@" + self.current_function_name + "$END" +
                           str(current_label_counter_value) + "\n")
            self.out.write("0;JMP\n")
            self.write_label("PUT_TRUE" + str(current_label_counter_value))
            self.out.write("@SP\n")
            self.out.write("M = M-1\n")
            self.out.write("A = M-1\n")
            self.out.write("M = -1\n")
            self.write_label("END" + str(current_label_counter_value))

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
