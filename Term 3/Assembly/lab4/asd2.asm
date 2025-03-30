
assume CS:code, DS:data, SS:stk
include emu8086.inc
; How to use CS?????

; 64 bytes
stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends


; Variables
data segment 
    msg1 db "fu$"
data ends 

code segment

    
; Main
start:
    ; Load variables
    mov AX, data
    mov DS, AX
    mov AX, 0
    ; Code

    lea si, msg1
    mov dx, [si]
    mov AH, 09h
    int 21h


    ; Out to DOS
    mov AH, 4Ch
    int 21h

code ends
end start 

