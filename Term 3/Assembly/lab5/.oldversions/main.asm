assume CS:code, DS:data, SS:stk
; include Kernel32.Lib
include emu8086.inc

; 64 bytes
stk segment STACK 'STACK'
        dw 32 dup(0)
stk ends


; Variables
data segment
    max_digits  equ 11
    num1_list db  max_digits+1 dup("$")
    num2_list db  max_digits+1 dup("$")
data ends

; Print linebreak
printBR macro
    mov DL, 13
    mov AH, 02h
    int 21h

    mov DL, 10
    mov AH, 02h
    int 21h
endm

; Get char into AL. 
; Push 1 if enter pressed and 0 otherwise
scan_char MACRO
    local ent_not_pressed, bs_not_pressed, exit

    ; get char from keyboard
    ; into AL:
    MOV AH, 00h
    INT 16h
    ; and print it:
    MOV AH, 0Eh
    INT 10h

    ; check for BS key
    CMP     AL, 8                       ; 'BACKSPACE' pressed?
    jne bs_not_pressed
                                          ; add iteration to scan loop
        PUTC    ' '                     ; clear position.
        PUTC    8                       ; backspace again.
    bs_not_pressed:

    ; ; check for ENTER key:
    CMP     AL, 13  ; carriage return?
    jne ent_not_pressed
    ;     ; Print enter (after carriage return)
        mov DL, 10
        mov AH, 02h
        int 21h
        push 1
        jmp exit
    ent_not_pressed:

    ; Return 0 to continue input
    push 0

    exit:
ENDM

; scan_char_10 macro 
;     scan_char
; endm

; ; Scan unsigned integer to dest variable
; my_scan_num_10 MACRO dest

; ENDM

; remove_bad_symbol macro       
;     PUTC    8       ; backspace.
;     PUTC    ' '     ; clear last entered not digit.
;     PUTC    8       ; backspace again.   
; endm

; ; Push 1 if first char is minus
; my_scan_num_minus macro 
;     local negative, no_exit

;     scan_char
;     pop ax
;     cmp ax, 0
;     je no_exit
;         exitm
;     no_exit:
;         cmp al, '-'
;         je negative
;             push 0
;             exitm
;         negative: 
;             push 1
; endm

; my_scan_num macro dest, numeric_system
;     push ax
;     my_scan_num_minus

;     if numeric_system eq 10

;     elseif numeric_system eq 16

;     else 
;         exitm
;     endif
; endm

scan_str macro dest, maxsize
    local cycle, endcycle, ent_not_pressed, bs_not_pressed
    mov cx, 0
    lea SI, dest
    cycle: 
        xor ax, ax 
        
        ; get char from keyboard
        ; into AL:
        MOV AH, 00h
        INT 16h
        ; and print it:
        MOV AH, 0Eh
        INT 10h
        
        
        ; check for BS key
        CMP     AL, 8                       ; 'BACKSPACE' pressed?
        jne bs_not_pressed            
            PUTC    ' '                     ; clear position.
            PUTC    8                       ; backspace again.
            cmp cx, 0
            je cycle
            dec cx
            jmp cycle                       ; add iteration to scan loop
        bs_not_pressed:

        ; ; check for ENTER key:
        CMP     AL, 13  ; carriage return?
        jne ent_not_pressed
        ;     ; Print enter (after carriage return)
            mov DL, 10
            mov AH, 02h
            int 21h
            jmp endcycle
        ent_not_pressed:

        xor ah, ah
        mov [SI], ax
        inc SI
        inc CX
        cmp CX, maxsize
        je endcycle
    jmp cycle
    endcycle:

endm
code segment
    ; Main
    start:
    ; Load variables
          mov             AX, data
          mov             DS, AX
          mov             AX, 0
    ; Code
    DEFINE_PRINT_NUM_UNS
    DEFINE_PRINT_NUM

    ; DEFINE_SCAN_NUM_FOR <num1_list>
    ; call SCAN_NUM_FOR_num1_list
    scan_str num1_list, 2
    
    ; scan_char


    ; Out to DOS
          mov             AH, 4Ch
          int             21h

code ends
end start 

