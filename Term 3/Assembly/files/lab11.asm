; Вопросы: Есть ли какие-то стандарты оформления кода; Как правильно писать ифы и циклы; Нормально что до 256 сделал;

assume CS:code,DS:data

data segment 
    ; 8 * a / b + (c + d) / 2
    a db 10
    b db 2
    c db 3
    d db 1

    X db 10
    XVI db 16

    frac1 dw ?
    frac2 dw ?
    res dw ?

    stringSize equ 5
    string db "?????", "$"
    ; string db ?, ?, ?, ?, ?,'$'
data ends 

code segment
program:
; Load variables
start:
    mov AX, data
    mov DS, AX
    mov AX, 0
; Calculation
calc:
    ; 8*a
    mov AL, a
    shl AL, 3

    ; / b
    mov BL, b  
    div BL    

    mov frac1, AX

    mov AL, c
    mov BL, d

    ; c+d
    add AL, BL

    ; /2
    shr AL, 1

    mov frac2, AX

    ; frac1+frac2
    mov AX, frac1
    mov BX, frac2

    add AX, BX

    mov res, AX
; Load string
go_10:
    lea SI, string
    mov CX, 0
; Fill string with res in 10 Nsystem
loop_10:
    xor AH, AH
    ; string=string + remainder
    div X
    add AH, 30h
    mov [SI + stringSize - 1], AH
    dec SI
    inc CX
    ; if AH != 0 => loop_10
    cmp AL, 0
    jne loop_10 
    
; Display string
print_10:
    ; Shift SI
    add SI, CX
    mov AX, stringSize
    sub AX, CX
    add SI, AX

    ; Print SI
    mov AH, 09h
    mov DX, SI
    int 21h
; Load string
go_16:
    ; Clear string for no reason
    mov AL, "?"
    clear_string_loop:
        add SI, CX
        mov [SI - 1], AL
        sub SI, CX
        loop clear_string_loop

    lea SI, string
    mov CX, 0
    mov AX, res
; Fill string with res in 16 Nsystem
loop_16:
    xor AH, AH
    ; string=string + remainder
    div XVI

    ; Fix if digits are letters 
    _if: 
        cmp AH, 10
        jl _then
        jge _else
    _then: 
        add AH, 30h
        jmp _endif
    _else:
        add AH, 41h - 10
        jmp _endif
    _endif:
    
    mov [SI + stringSize - 1], AH
    dec SI
    inc CX
    ; if AH != 0 => loop_16
    cmp AL, 0
    jne loop_16

print_16:
    ; Print linebreak
    mov DL, 10
    mov AH, 02h
    int 21h

    ; Shift SI
    add SI, CX
    mov AX, stringSize
    sub AX, CX
    add SI, AX

    ; Print SI
    mov AH, 09h
    mov DX, SI
    int 21h
exit:
    ; Out to DOS
    mov AH, 4Ch
    int 21h
code ends
end program 

