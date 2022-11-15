"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        if mnemonic == "null":
            return "000"
        if mnemonic == "M":
            return "001"
        if mnemonic == "D":
            return "010"
        if mnemonic == "MD":
            return "011"
        if mnemonic == "A":
            return "100"
        if mnemonic == "AM":
            return "101"
        if mnemonic == "AD":
            return "110"
        if mnemonic == "AMD":
            return "111"

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 7-bit long binary code of the given mnemonic.
        """
        a = "0"
        mnemonicX = mnemonic
        if "M" in mnemonic:
            mnemonicX = mnemonic.replace("M", "A")
            a = "1"
        if mnemonicX == "0":
            return a + "101010"
        if mnemonicX == "1":
            return a + "111111"
        if mnemonicX == "-1":
            return a + "111010"
        if mnemonicX == "D":
            return a + "001100"
        if mnemonicX == "A":
            return a + "110000"
        if mnemonicX == "!D":
            return a + "001101"
        if mnemonicX == "!A":
            return a + "110001"
        if mnemonicX == "-D":
            return a + "001111"
        if mnemonicX == "-A":
            return a + "110011"
        if mnemonicX == "D+1":
            return a + "011111"
        if mnemonicX == "A+1":
            return a + "110111"
        if mnemonicX == "D-1":
            return a + "001110"
        if mnemonicX == "A-1":
            return a + "110010"
        if mnemonicX == "D+A":
            return a + "000010"
        if mnemonicX == "D-A":
            return a + "010011"
        if mnemonicX == "A-D":
            return a + "000111"
        if mnemonicX == "D&A":
            return a + "000000"
        if mnemonicX == "D|A":
            return a + "010101"


    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        if mnemonic == "null":
            return "000"
        if mnemonic == "JGT":
            return "001"
        if mnemonic == "JEQ":
            return "010"
        if mnemonic == "JGE":
            return "011"
        if mnemonic == "JLT":
            return "100"
        if mnemonic == "JNE":
            return "101"
        if mnemonic == "JLE":
            return "110"
        if mnemonic == "JMP":
            return "111"
