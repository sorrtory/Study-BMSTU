assume CS:code, DS:data, SS:stk
include emu8086.inc
; How to use cs?
; How to use db/dw ouside data section


; 64 bytes
stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends

def MACRO x, t, n, v
    ; Check for params existance
    i=1
    badparam=0
    irp param, <&x, &t, &n>                 ; for i in args
        ifb <param>                         ; if i is emty
            badparam=1
            exitm
        endif
        i=i+1
    endm

    if badparam                             ; have no params. exit
        printMsg %i
        printMsg < parameter is unset>
        printBR
        printMsg Exit
        exitm
    endif

    ifb <v>
        &x d&t &n dup("u")
    else
        &x d&t &n dup(&v)
    endif
ENDM

; Variables
data segment 
    A dw 10h
    B db 10
    C db 30h
    D db -40h
    E dw -50h
    F db 60h

    aba db 10 dup("z"), '$'
    def aboba, b, 10

data ends 


code segment

; Print linebreak
printBR macro
    mov DL, 13
    mov AH, 02h
    int 21h

    mov DL, 10
    mov AH, 02h
    int 21h
endm
    
; Print message
printMsg macro msg
    irpc char, <msg>
        mov dl, '&char'
        mov AH, 02h
        int 21h
    endm

    ; irpc character,<строка символов>
    ;     db '&character&' ,OFh
    ; endm
endm

; Print num if it's byte
PRINT_BYTE_10 macro num
    local print, cycle

    mov cx, 0
    mov al, num
    mov bl, 10

    cycle:
        mov ah, 0 
        cmp al, 0
        je print
    
        div bl ; al=ax/10 ; ah=remainder
        push ax
        inc cx
    jmp cycle

    print:
        pop ax
        add ah, '0'
        mov dl, ah
        mov ah, 02h
        int 21h
    loop print
endm

; Print num if it's word
PRINT_WORD_10 macro num
    local print, cycle

    mov cx, 0
    mov ax, num
    mov bx, 10

    cycle:
        mov dx, 0 
        cmp ax, 0
        je print
    
        div bx ; ax=dx:ax/10 ; dx=remainder
        push dx
        inc cx
    jmp cycle

    print:
        pop ax
        add ax, '0'
        mov dx, ax
        mov ah, 02h
        int 21h
    loop print
endm


mainMacro MACRO A, B, C, D, E, F, mode
    ; Check for params existance
    i=1
    badparam=0
    irp param, <&A, &B, &C, &D, &E, &F>     ; for i in args
        ifndef param
            badparam=1
            exitm
        endif
        ifb <param>                         ; if i is emty
            badparam=1
            exitm
        endif
        i=i+1
    endm

    if badparam                             ; have no params. exit
        printMsg %i
        printMsg < parameter is unset>
        printBR
        printMsg Exit
        exitm
    endif
    
    ; Run a) or b)
    if &mode eq 1 or &mode eq 0
        ; Add 1 for bytes
        irp param, <&A, &B, &C, &D, &E, &F>     ; for i in args
            if type param eq 1
                add param, 1
            else
                add param, 2
            endif
        endm
    elseif &mode eq 2
        irp param, <&A, &B, &C, &D, &E, &F>     ; for i in args
            if type param eq 1
                mov param, -1
            endif
        endm
    ; elseif mode eq 3
    else
        .err "Bad mode$"
    endif
ENDM

print_sign MACRO num
    local less, endd
    ; mov ax, num
    movVarToReg a, l, num
    cmp al, 0
    jl less
    jmp endd
    less:
        neg al
        movRegToVar num, a, l
        printMsg -
    endd:

ENDM

print_10_sign macro num
    local less1, less2, end1, end2
    push ax
    if type num eq 1
        mov al, num
        cmp al, 0
        jl less1
        
        jmp end1
        less1:
            neg al
            mov num, al
            printMsg -
        end1:

        PRINT_BYTE_10 num
    elseif type num eq 2
        mov ax, num
        cmp ax, 0
        jl less2
        jmp end2
        less2:
            neg ax
            mov num, ax
            printMsg -
        end2:

        PRINT_WORD_10 num
    else
        ; printMsg <Can't print this type>
        PRINT_WORD_10 num
    endif

    pop ax
endm

print_10 macro num
    if type num eq 1
        PRINT_BYTE_10 num
    elseif type num eq 2
        PRINT_WORD_10 num
    else
        ; printMsg <Can't print this type>
        PRINT_WORD_10 num
    endif
endm

printArgs macro A, B, C, D, E, F
    ; Print params
    i=0
    irp paramm, <&A, &B, &C, &D, &E, &F>     ; for i in args
        printMsg <Param>
        printMsg %i
        printMsg < is >
        print_10 paramm
        printBR
        i=i+1 
    endm
endm

printArgs2 macro A, B, C, D, E, F
    ; Print params with signs
    i=0
    irp param, <&A, &B, &C, &D, &E, &F>     ; for i in args
        print 10
        print 13
        print "New param"
        mov ax, i
        call print_num
        print " is "
        movVarToReg a, l, param
        call print_num 
        ; print_10_sign param
        i=i+1
    endm
endm

; var = word/byte   ; variable of type word or byte
; reg = a/b/c/d     ; first letter of regestry
; reg_byte = l/h    ; set to low or high if type of var is byte
movRegToVar macro var, reg, reg_byte
    if type var eq 1
        mov var, &reg&reg_byte
    else
        mov var, &reg&x
    endif
endm

; reg = a/b/c/d     ; first letter of regestry
; reg_byte = l/h    ; set to low or high if type of var is byte
; var = word/byte   ; variable of type word or byte
movVarToReg macro reg, reg_byte, var
    if type var eq 1
        mov &reg&reg_byte, var
    else
        mov &reg&x, var
    endif
endm

;;; cbw


; Push a size of param
regtype MACRO reg
    ; Handle 8-bit general-purpose registers
    IF reg EQ AL or reg EQ BL or reg EQ CL or reg EQ DL
        push 1
    ; Handle 16-bit general-purpose registers
    ELSEIF reg EQ AX or reg EQ BX or reg EQ CX or reg EQ DX
        push 2
    ; Handle 16-bit index registers
    ELSEIF reg EQ SI or reg EQ DI or reg EQ BP or reg EQ SP
        push 2
    ; Handle variables
    ELSE
        .err "Unknown reg"
    ENDIF
ENDM



; Main
start:
    ; Load variables
    mov AX, data
    mov DS, AX
    mov AX, 0
    ; Code
    DEFINE_SCAN_NUM
    DEFINE_PRINT_NUM
    DEFINE_PRINT_NUM_UNS  ; требуется для print_num.
    
    
    ;;; Task 0
    ; Input params
    ; i=0
    ; irp param, <A, B, C, D, E, F>     ; for i in args
    ;     print "Enter param "
    ;     mov ax, i+1
    ;     CALL PRINT_NUM                ; print ax
    ;     print ": "
    ;     call scan_num                 ; scan to cx
    ;     ; param is word or byte
    ;     movRegToVar param c l
    ;     printn 13
    ;     i=i+1 
    ; endm
    ; printBR

    ;;; Task 1
    ; printArgs A B C D E F           ; Unsigned print
    ; mainMacro A B C D E F 1
    ; printArgs2 A B C D E F          ; Signed print

    ; ;; Task 2
    ; printArgs A B C D E F             ; Unsigned print
    ; mainMacro A, B, C, D, E, F, 1
    ; printArgs2 A B C D E F            ; Signed print


    ;;; Task 3    
    mov cx, length aboba
    lea si, aboba
    cyc:
        mov dl, [si]
        ; putc [si]
        mov ah, 02h
        int 21h
        inc si
    loop cyc
    PUTC ""

    mov AH, 4Ch
    int 21h

code ends
end start 

