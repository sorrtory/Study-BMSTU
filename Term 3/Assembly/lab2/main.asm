assume CS:code,DS:data

data segment 
    ; DATA
    numbers db 1, 0, 3, 4, 5, 6, 20, 8, 9, 10, 11, 12
    elemSize = 4
    numbersLength = 12
    max db 0
    maxIndex db 0
    currentIndex db 0

    ; For output
    X db 10
    stringSize equ 3
    string db "???", "$"

data ends 


code segment
; Print AX value in 10 system
print10 proc
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

    ; Print linebreak
    mov DL, 10
    mov AH, 02h
    int 21h

    ret
print10 endp

start:
    ; Load variables
    mov AX, data
    mov DS, AX
    mov AX, 0
    ; Code
    lea SI, numbers
    mov CX, numbersLength

    ; Go through numbers
    go_numbers:
        mov AL, byte ptr [SI]
        mov AH, max
        inc SI

        cmp AL, AH
        jg greater
        jl fi

        greater: 
            mov AH, currentIndex
            mov maxIndex, AH
            mov max, AL
            jmp fi
        fi:
    
        mov AL, currentIndex
        inc AL
        mov currentIndex, AL

    loop go_numbers

    xor AX, AX
    mov AL, max
    call print10

    mov AL, maxIndex
    call print10

    ; Out to DOS
    mov AH, 4Ch
    int 21h
code ends
end start 

