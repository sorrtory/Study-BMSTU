assume CS:code, DS:data, SS:stk
include emu8086.inc
; How to use CS?????

; 64 bytes
stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends


; Variables
data segment 
data ends 

code segment

    
; Main
start:
    ; Load variables
    mov AX, data
    mov DS, AX
    mov AX, 0
    ; Code




    ; Out to DOS
    mov AH, 4Ch
    int 21h

code ends
end start 

