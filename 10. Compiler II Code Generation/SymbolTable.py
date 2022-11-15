"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

STATIC = "static"
FIELD = "field"
VAR = "local"
ARG = "argument"
ERR = "INVALID IDENTIFIER!"
POINTER = "pointer"
ERR_INDEX = -1
TYPE = 0
KIND = 1
INDEX = 2


class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table.
        class hash - name: identifier ,kind: field or static
        subroutine_hash  - name: identifier, kind: local, argument
        type for all: int, char, boolean and classes
        """

        self.class_hash = {}
        self.subroutine_hash = {}
        self.count_local, self.count_argument, self.count_field, self.count_static = (0, 0, 0, 0)

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_hash = {}
        self.count_local, self.count_argument = (0, 0)

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """

        if kind in [STATIC, FIELD]:
            self.class_hash[name] = (type, kind, self.var_count(kind))
            self._increase_counter(kind)
        elif kind in [ARG, VAR]:
            self.subroutine_hash[name] = (type, kind, self.var_count(kind))
            self._increase_counter(kind)

    def _increase_counter(self, kind):
        if kind == STATIC:
            self.count_static += 1
        elif kind == FIELD:
            self.count_field += 1
        elif kind == VAR:
            self.count_local += 1
        elif kind == ARG:
            self.count_argument += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """

        if kind == STATIC:
            return self.count_static
        elif kind == FIELD:
            return self.count_field
        elif kind == VAR:
            return self.count_local
        elif kind == ARG:
            return self.count_argument

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # Your code goes here!
        if name in self.subroutine_hash:
            return self.subroutine_hash[name][KIND]
        elif name in self.class_hash:
            return self.class_hash[name][KIND]
        return ERR

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_hash:
            return self.subroutine_hash[name][TYPE]
        elif name in self.class_hash:
            return self.class_hash[name][TYPE]
        return ERR

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_hash:
            return self.subroutine_hash[name][INDEX]
        elif name in self.class_hash:
            return self.class_hash[name][INDEX]
        return ERR_INDEX
