assume CS:code, DS:data, SS:stk

stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends

data segment 
    ; DATA
    maxLen equ 20
    string db maxLen dup("$") ; НЕВЕРНО ЗАДАЮ СТРОКУ
    ; string db maxLen, maxLen-1  dup("$")
    copiedString db maxLen dup("$")
    enterMSG db "Enter string: $"
    enteredMSG db "Inputted: $"
    outMSG1 db "Result of copy: $"
    outMSG2 db "Searching pattern: $"
    outMSG3 db "Result of searching: $"
    sn dw ?, '$'
    ab db "ab$"

data ends 


code segment

; Print linebreak
printBR proc
    mov DL, 10
    mov AH, 02h
    int 21h
    ret
printBR endp
    
; Print DX
printDX proc
    mov AH, 09h
    int 21h
    ret
printDX endp

; char * strcpy ( char * destination, const char * source );
strcpy proc
    push BP
    mov BP, SP


    mov SI, [BP+4]
    mov DI, [BP+6]

    
    xor AX, AX
    mov CX, 0
    for_SI:
        mov AL, byte ptr [SI]
        cmp AL, '$'
        je for_SI_Done
        mov [DI], AL
        
        inc SI
        inc DI
        inc CX
        jmp for_SI
    for_SI_Done:
    sub SI, CX
    sub DI, CX

    pop BP
    pop AX
    push DI
    push AX
    ret
strcpy endp

strlen proc
    push BP
    mov BP, SP
    
    mov SI, [BP + 4]    ; String ptr
    xor CX, CX          ; Counter
    xor AX, AX          ; Char
    .Len1:
        mov AL, byte ptr [SI]
        cmp AL, '$'
        je .Len2
        inc CX
        inc SI
        jmp .Len1
    .Len2:
    sub SI, CX
    
    pop BP
    pop AX
    push CX
    push AX
    ret
strlen endp


;                       haystack         needle
; char *strstr(const char *strB, const char *strA);
strstr proc
    push BP
    mov BP, SP
    sub SP, 6 ; 3 local vars
    ; Code
    mov SI, [BP+6] ; haystack
    mov DI, [BP+4] ; needle
    
    mov byte ptr [BP-2], 0 ; Len SI - Len DI
    mov byte ptr [BP-4], 0 ; Len DI - 1

    push [BP+6]
    call strlen
    pop [BP-2]

    push [BP+4]
    call strlen
    pop [BP-4]

    mov AH, byte ptr [BP-2]
    mov AL, byte ptr [BP-4]
    sub AH, AL
    mov byte ptr [BP-2], AH

    ; for i=0...|haystack|-|needle|
    ;   for j=0...|needle|
    ;     if haystack[i+j]<>needle[j] 
    ;       then goto 1
    ;   output("Найдено: ", i+1)
    ;   1:

    mov CL, 0 ; i
    mov CH, 0 ; j
    xor AX, AX
    mov AL, 255 ; Not finded value
    xor BX, BX
    .L1:
        cmp CL, byte ptr [BP-2]
        je .L1_Done

        mov CH, 0
        mov BX, 0
        mov BL, CL
        add SI, BX
        .L2:
            mov BX, 0
            cmp CH, byte ptr [BP-4]
            je .L2_Done
            
            mov BH, byte ptr [DI]
            mov BL, byte ptr [SI]
            cmp BL, BH
            jne .NotFinded 

            inc SI
            inc DI

            inc CH
            jmp .L2
        .L2_Done:
        mov AL, CL

        .NotFinded:
        mov SI, [BP+6]
        mov DI, [BP+4]

        inc CL
        jmp .L1
    .L1_Done:

    mov SP, BP
    pop BP
    pop BX
    push AX
    push BX
    ret
strstr endp


; Main proc
start:
    ; Load variables
    mov AX, data
    mov DS, AX
    mov AX, 0
    ; Code

    ; Print msg
    lea DX, enterMSG
    call printDX
    
    ; Input string
    mov AH, 10
    lea DX, string
    ; mov string, maxLen ; No need?
	int 21h
    call printBR

    ; Print msg
    lea DX, enteredMSG
    call printDX

    ; Print string
    lea DX, string + 2
    call printDX
    call printBR

    ; Call strcpy
    lea DX, copiedString
    push DX    
    lea DX, string + 2
    push DX
    call strcpy


    ; Print msg
    lea DX, outMSG1
    call printDX

    ; Print result
    pop DX
    call printDX
    call printBR

    ; Print ab
    lea DX, outMSG2
    call printDX
    lea DX, ab
    call printDX
    call printBR

    ; Print outmsg3
    lea DX, outMSG3
    call printDX

    ; Call strstr
    lea DX, string + 2
    push DX
    lea DX, ab
    push DX
    call strstr
    pop AX

    ; Print char result of strstr
    add ax, '0'
    lea SI, sn
    mov word ptr [SI], ax
    mov DX, SI
    call printDX

    ; Out to DOS
    mov AH, 4Ch
    int 21h
code ends
end start 

