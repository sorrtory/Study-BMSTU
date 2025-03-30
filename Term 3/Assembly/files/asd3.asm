assume CS:code, DS:data, SS:stk

stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends

data segment 
    ; DATA
    maxLen equ 20
    string db maxLen dup("$")
    copiedString db maxLen dup("$")
    enterMSG db "Enter string: $"
    enteredMSG db "Inputted: $"
    outMSG db "Result: $"

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
    pop BP
    pop SI
    pop DI
    ; OLD STACK OPERATIONS
    ; push BP
    ; mov BP, SP

    ; mov SI, [BP+4]
    ; mov DI, [BP+6]
    
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

    ; OLD STACK OPERATIONS
    ; push [BP+6]
    ; pop BX

    sub DI, CX
    push DI
    push BP
    ret
strcpy endp

strlen proc
    push AL
    push CX
    xor AL, AL ; Char
    xor CX, CX ; Counter
    for_str_lenCnt:
        mov AL, byte ptr [SI]
        cmp AL, '$'
        je for_str_lenCnt_Done
        inc CX
        inc SI
        jmp for_str_lenCnt
    for_str_lenCnt_Done:
    sub SI, CX



strlen endp
; char *strstr(const char *strB, const char *strA);
strstr proc
    pop BP
    pop DI
    pop SI
    push BP

    xor CX, CX ; Result index
    xor AH, AH ; SI len
    xor AL, AL ; SI char
    xor BH, BH ; DI len
    xor BL, BL ; DI char

    for_SI_lenCount:
        mov AL, byte ptr [SI]
        cmp AL, '$'
        je for_SI_lenCount_Done
        inc AH
        inc SI
        jmp for_SI_lenCount
    for_SI_lenCount_Done:
    sub SI AH

    for_SI_lenCount:
        mov AL, byte ptr [SI]
        cmp AL, '$'
        je for_SI_lenCount_Done
        inc AH
        inc SI
        jmp for_SI_lenCount
    for_SI_lenCount_Done:
    sub SI AH
    ; for_SI:
    ;     mov AL, byte ptr [SI]
    ;     ; Out of cycle if SI ended
    ;     cmp AL, '$'
    ;     je for_SI_Done

    ;     ; ; Check for occurence
    ;     ; add DI, BL
    ;     ; mov AH, byte ptr [DI]
    ;     ; cmp AL, AH ; AL - char from source string, AH - char from sample to find string
    ;     ; jne neq
    ;     ; eq:
    ;     ;     mov AH, byte ptr [DI + 1]
    ;     ;     ; out of cycle if DI ended
    ;     ;     cmp AH, "$"
    ;     ;     jne ahNotEnded
    ;     ;     ahEnded:
    ;     ;         je for_SI_Done

    ;     ;     ahNotEnded:

    ;     ;     inc CX
    ;     ;     inc SI
    ;     ;     jmp for_SI
    ;     ; neq:
    ;     ;     cmp CX, 0
    ;     ;     jne cxIsNotZero
    ;     ;     cxIsZero:
    ;     ;         inc SI
    ;     ;         jmp endCxIs
    ;     ;     cxIsNotZero:
    ;     ;         mov CX, 0
    ;     ;         jmp for_SI
    ;     ;     endCxIs:

    ;     ; endif:
        
    ;     ; inc SI
    ;     ; jmp for_SI
    ; for_SI_Done:
    

    ; Return
    cmp AH, 0
    jne finded
    not_finded:

    finded:

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

    ; Call function
    lea DX, copiedString
    push DX    
    lea DX, string + 2
    push DX
    call strcpy

    ; Print msg
    lea DX, outMSG
    call printDX

    ; Print result
    ; lea DX, copiedString
    pop DX
    call printDX

    ; Out to DOS
    mov AH, 4Ch
    int 21h
code ends
end start 

