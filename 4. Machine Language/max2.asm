@R1
D = M
@R2
D = D - M
@POS
D;JGE
@R2
D = M
@R0
M = D
@END
0;JMP
(POS)
@R1
D = M
@R0
M = D
(END)
@END
0;JMP