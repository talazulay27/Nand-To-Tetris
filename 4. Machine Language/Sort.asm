// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort. 

// Put your code here.

// i = 0
//for (i; i< len(A);i++):
// j = 0
//  for (j=0;j<len(A)-i;j++):
//      if (A[j]<A[j+1]):
//            swap


@i
M=0
(LOOP)
    @j
    M=0
    (INNERLOOP)
        @j
        D = M
        @R14
        A = M+D
        D = M // D = A[j]
        A = A+1
        D = D-M // D = A[j] - A[j+1]
        
        @SKIPSWAP
        D;JGT
        
        @j
        D = M
        @R14
        A = M+D
        D = M // D = A[j]
        @temp// A = A[j]
        M = D // temp = A[j]
        @j
        D = M
        @R14
        A = M+D
        A = A+1 // A[j+1]
        D = M // D = A[j+1]
        A = A-1
        M = D // A[j] = A[j+1]
        A = A+1
        D = A
        @temp2
        M = D // temp2 = ind of A[j+1]
        @temp
        D = M
        @temp2
        A = M
        M = D
        

        
        (SKIPSWAP)
        @R15
        D = M
        @i
        D = D-M
        @j
        M = M+1
        D = D-M
        D = D-1
        @INNERLOOP
        D;JGT

    //for (i; i< len(A);i++)
    @R15
    D = M
    @i
    M = M+1
    D = D-M
    @LOOP
    D;JGT
   @END
    0;JMP
(END)
    @END
    0;JMP


