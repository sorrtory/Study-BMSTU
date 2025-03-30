assume CS:code, DS:data, SS:stk

; 64 bytes
stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends


; Variables
data segment 

data ends 

code segment

; Procedure with args
procedure proc
    push BP
    mov BP, SP
    sub SP, 4 ; 2 local vars
    ; Code
    mov byte ptr [BP-2], 1 ; Local variable 1
    mov byte ptr [BP-4], 2 ; Local variable 2

    mov BL, [BP+6] ; Procedure argument 1
    mov AL, [BP+4] ; Procedure argument 2

    mov SP, BP
    pop BP
    ret
procedure endp
; ; Calling procedure
; push 1
; push 2
; call procedure

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

