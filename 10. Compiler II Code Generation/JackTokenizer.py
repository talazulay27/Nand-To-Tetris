"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORD = "keyword"
SYMBOL = "symbol"
IDENTIFIER = "identifier"
INT_CONST = "integerConstant"
STRING_CONST = "stringConstant"
MIN_NUMBER = 0
MAX_NUMBER = 32767


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.token_types = [SYMBOL, STRING_CONST, INT_CONST]
        self.keywords = ["class", "constructor", "function", "method", " field", "static",
                         "var", "int", "char", "boolean", "void", "true", "false", "null", "this",
                         "let", "do", "if",
                         "else", "while", "return"]
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|',
                        '<', '>', '=', '~',
                        '^', '#']
        self.special_symbols = {'<': "lt;", '>': "gt;", '^': "shiftleft", '#': "shiftright",
                                '~': 'not', '-': 'neg'}

        input_lines = [line.strip() for line in input_stream.read().splitlines()]
        lines_with_no_comments = []
        line_indx = 0
        while line_indx < len(input_lines):
            start_comment_index = input_lines[line_indx].find("/*")
            start_api_comment_index = input_lines[line_indx].find("/**")
            find_backslashes = input_lines[line_indx].find("//")
            start_string = input_lines[line_indx].find('"')
            end_string = input_lines[line_indx].find('"', start_string + 1)
            flag_string = False
            if start_string != -1 and end_string != -1:
                flag_string = True
            if start_comment_index != -1:
                end_comment_index = input_lines[line_indx].find("*/")
                if flag_string and start_string < start_comment_index < end_string:
                    lines_with_no_comments.append(input_lines[line_indx])
                    line_indx += 1
                    continue
                while end_comment_index == -1:
                    line_indx += 1
                    end_comment_index = input_lines[line_indx].find("*/")
                input_lines[line_indx] = input_lines[line_indx][:start_comment_index] + \
                                         input_lines[line_indx][end_comment_index + 2:]

            elif start_api_comment_index != -1:
                end_api_comment_index = input_lines[line_indx].find("*/")
                if flag_string and start_string < start_api_comment_index < end_string:
                    lines_with_no_comments.append(input_lines[line_indx])
                    line_indx += 1
                    continue
                while end_api_comment_index == -1:
                    line_indx += 1
                    end_api_comment_index = input_lines[line_indx].find("*/")
                input_lines[line_indx] = input_lines[line_indx][:start_api_comment_index] + \
                                         input_lines[line_indx][end_api_comment_index + 2:]
            elif find_backslashes != -1:
                if flag_string and start_string < find_backslashes < end_string:
                    lines_with_no_comments.append(input_lines[line_indx])
                    line_indx += 1
                    continue
                input_lines[line_indx] = input_lines[line_indx][:find_backslashes]

            else:
                lines_with_no_comments.append(input_lines[line_indx])
                line_indx += 1
        lines_with_no_comments_and_tabs = [line.strip() for line in lines_with_no_comments]
        lines_with_no_white_space = []
        for line in lines_with_no_comments_and_tabs:
            if '"' not in line:
                lines_with_no_white_space.append(line.split())
            else:
                lines_with_no_white_space.append(line.split('"')[0].split())
                lines_with_no_white_space.append(['"' + line.split('"')[1] + '"'])
                lines_with_no_white_space.append(line.split('"')[2].split())

        tokens_before_symbol = []
        [tokens_before_symbol.extend(token) for token in lines_with_no_white_space]

        self.tokens = []
        for token in tokens_before_symbol:
            if '"' in token:
                self.tokens.append(token)
                continue
            else:
                flag = False
                for symbol in self.symbols:
                    if symbol in token:
                        flag = True
            if flag:
                self.remove_symbols(token)
            else:
                self.tokens.append(token)

        self.total_tokens = len(self.tokens)
        self.tokens_counter = 0
        self.current_token = self.tokens[self.tokens_counter]

    def get_next_token(self):
        if self.tokens_counter + 1 < self.total_tokens:
            return self.tokens[self.tokens_counter + 1]
        return ""

    def remove_symbols(self, token):
        last_symbol_index = 0
        for i in range(len(token)):
            if token[i] in self.symbols:
                if last_symbol_index != i:
                    self.tokens.append(token[last_symbol_index:i])

                self.tokens.append(token[i])
                last_symbol_index = i + 1
        if (last_symbol_index < len(token)):
            self.tokens.append(token[last_symbol_index:len(token)])

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.tokens_counter < self.total_tokens

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        self.tokens_counter += 1
        if self.has_more_tokens():
            self.current_token = self.tokens[self.tokens_counter]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current_token in self.keywords:
            return KEYWORD
        elif self.current_token in self.symbols:
            return SYMBOL
        elif self.current_token.isnumeric() and (
                MIN_NUMBER <= int(self.current_token) <= MAX_NUMBER):
            return INT_CONST
        elif self.current_token[0] == '"' and self.current_token[-1] == '"':
            return STRING_CONST
        else:
            return IDENTIFIER

    def keyword(self) -> str:

        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """

        return self.current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """

        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.current_token.replace('"', '')
