assume CS:code, DS:data, SS:stk
include emu8086.inc


; 64 bytes
stk segment STACK 'STACK'
    dw 32 dup(0)
stk ends


; Variables
data segment 
    max_digits  equ 11
    num1_list db  max_digits, max_digits+2 dup("$")
    num2_list db  max_digits, max_digits+2 dup("$")

    placeholder equ '$' ; Better use $, because num list is string at first
    ; Numlist is byte list with following pattern
    ; [minus?][length]...(<=max_digits)...[numeric system (10|16)]

    ; Some examples. Comment prev declaration and input macro to use

    ; num1_list db 0, 3, 1, 0, 0, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, 10
    ; num2_list db 0, 3, 6, 5, 2, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, 10

    ; num1_list db 1, 3, 1, 0, 0, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, 10
    ; num2_list db 0, 1, 3, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, 10

    ; num1_list db 0, 2, 0, 1, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, 10
    ; num2_list db 1, 1, 1, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, placeholder, 10

    ; num1_list db  0, 3, 1, 0, 0, 8 dup(placeholder), 10
    ; num2_list db  1, 1, 9, 10 dup(placeholder), 10


    result_list db  0, max_digits, max_digits dup(placeholder), 10
    ; Used to add SI+DI
    num_list_buff db  0, max_digits, max_digits dup(placeholder), 10
    ; Used to add SI-1
    num_list_minus1 db  1, 1, 1, max_digits-1 dup(placeholder), 10
data ends 

code segment

; Print linebreak
printBR macro
    push AX
    push DX
    mov DL, 13
    mov AH, 02h
    int 21h

    mov DL, 10
    mov AH, 02h
    int 21h
    pop DX
    pop AX
endm

; Print the char in AL
printAL MACRO
    push AX
    push DX
    mov DL, AL
    mov AH, 02h
    int 21h
    pop DX
    pop AX
ENDM

; Print message
printMsg macro msg
    push AX
    push DX
    irpc char, <msg>
        mov dl, '&char'
        mov AH, 02h
        int 21h
    endm
    pop DX
    pop AX
endm

; Convert string list to num list
; Push 0 on success and 1 on error
; Input in 10 and 16 (uppercase A-F) num system.
; SI is string. SI[0] maxsize. SI[1] realsize. 
; After proc 
; SI[0] is minus flag. 
; SI[1] is realsize. 
; SI[2+max_digits] is numeric system
check_input PROC
    locals @@
    pop BP
    ; Set length
    mov cx, 0
    mov cl, byte ptr [SI + 1] 
    
    ; Set decimal system by default
    mov DI, SI
    add DI, 2
    add DI, max_digits
    mov byte ptr [DI], 10

    ; Set minus
    mov byte ptr [SI], 0
    cmp byte ptr [SI+2], '-'
    jne @@l1
    mov byte ptr [SI], 1
    ; Update length
    dec CX
    mov byte ptr [SI+1], CL
    ; Shift SI to left
    push SI
    push CX
    add SI, 3
    @@shift_cycle:
        mov AL, byte ptr [SI]
        dec SI
        mov byte ptr [SI], AL
        add SI, 2
    loop @@shift_cycle
    pop CX
    pop SI
    @@l1:

    add SI, 2
    @@cycle:
        ; Check the char is in [0, 9]
        cmp byte ptr [SI], '0'
        jge char_greater_0
        jmp @@bad_char
        
        char_greater_0:
        cmp byte ptr [SI], '9'
        jle good_char_10
        
        ; Check the char is in [A, F]
        cmp byte ptr [SI], 'A'
        jge char_greater_A
        jmp @@bad_char

        char_greater_A:
        cmp byte ptr [SI], 'F'
        jle good_char_16
        jmp @@bad_char

        
        good_char_10:
            ; Convert to dec
            sub byte ptr [SI], '0'
            jmp end_good
        good_char_16:
            ; Convert to hex
            sub byte ptr [SI], 'A'
            add byte ptr [SI], 10
            ; Set hex indicator
            mov byte ptr [DI], 16
        end_good:

        inc SI
    loop @@cycle
    push 0
    jmp @@exit
    @@bad_char:
        printMsg <Bad char: >
        PUTC [SI]
        printBR
        push 1
    @@exit:
    ; TODO:
    ; Crutch to get rid of D
    ; May corrupt system!!!!!
    mov byte ptr [SI], placeholder
    mov byte ptr [SI+1], placeholder
    push BP
    ret
check_input ENDP

; Set argument to SI by number
; List: reg with 1|2
get_argument macro list
    local l1, l3
    push BP
    cmp list, 1
    jne l1 
        add BP, 6
        jmp l3
    l1: 
        add BP, 4
    l3:
    mov SI, word ptr [BP]
    pop BP
endm

; Move the digit of list to dest
; List: reg with 1|2
; Dest: 8-bit reg
; Digit: 16-bit within [0, maxlen]
set_digit_to_reg macro list, dest, digit
    get_argument list

    add SI, digit
    mov &dest&, byte ptr [SI]
    sub SI, digit
endm


; Print num_list from SI
print_num_list proc
    locals @@
    push CX
    push AX
    push SI


    cmp byte ptr [SI], 1
    jne @@l1
        mov AL, '-'
        printAL
    @@l1:
    mov CX, 0
    ; mov CL, max_digits+1          ; Max length and system
    mov CL, byte ptr [SI+1]  ; Length of num list
    cmp CL, 0
    jg @@gocycle
    printMsg <Num list is empty>
    jmp @@endcycle
    @@gocycle:
    add SI, 2                ; SI is incrementable
    @@cycle:
        xor ax, ax
        mov al, byte ptr [SI]
        cmp al, 9
        jg @@sixteen
            add al, '0'
            printAL
            jmp @@anyway
        @@sixteen:
            sub al, 10
            add al, 'A'
            printAL
        @@anyway:
        inc SI
    loop @@cycle 
    @@endcycle:

    pop SI
    ; Print length
    mov AX, 0
    mov AL, byte ptr [SI+1]  ; Length of num list
    printMsg < (>
    call print_num
    printMSG <)>

    pop AX
    pop CX
    ret
print_num_list endp

; If ah >= system
; Subtract system from from ah
; Mov 1 to next byte of [DI]
add_byte_exceed macro system
    local l1

    cmp ah, system
    jl l1
        ; If exceed the system
        ; Add 1 for next place
        mov byte ptr [DI+1], 1
        ; Subtract system value from byte sum
        sub ah, system
    l1:
endm

; Add bytes from AH and AL
; Set result to DI from left to rigth
add_byte MACRO system
    local l2, l3, l4, l5
  
    ; Set ah+al to ah
    add ah, al
    ; Check for system excess
    add_byte_exceed system
    ; Check if place is unused
    cmp byte ptr [DI], placeholder
    jne l2
        ; If placeholder at result place
        mov byte ptr [DI], ah
        jmp l3
    l2:
        ; If 1 at result place
        add byte ptr [DI], ah
        mov ah, byte ptr [DI]

        ; Check for system excess
        add_byte_exceed system
        mov byte ptr [DI], ah
    l3:
ENDM


; Sub AL from DI
; Set result to DI
; Take deficient from left to rigth of DI
sub_byte MACRO system
    local l1, l2
    mov ah, byte ptr [DI]
    sub ah, al
    ; Check for negative result
    l1:
    cmp ah, 0
    jge l2
        ; Less than 0    
        ; Take system value from higher place
        sub byte ptr [DI+1], 1
        add ah, system
        ; Check again
        jmp l1
    l2:
    ; Set result to place
    mov byte ptr [DI], ah
ENDM

; Reverse num list digits
reverse_num_list MACRO list
    local cycle
    push AX
    push CX
    push SI
    push DI

    mov AX, 0               ; Buffer for swap
    mov SI, list            ; Pointer to list head
    mov CX, 0               ; Length of list 
    mov CL, byte ptr [SI+1] ; Length of list 
    mov DI, list            ; Pointer to list rear
    add DI, 1
    add DI, CX
    
    ; Set CL to half length
    mov AL, byte ptr [SI+1]
    mov CH, 2
    div CH
    mov CH, 0
    mov CL, AL

    add SI, 2
    cycle:
        mov AH, byte ptr [SI]
        mov AL, byte ptr [DI]

        mov byte ptr [SI], AL
        mov byte ptr [DI], AH

        inc SI
        dec DI
    dec cl
    cmp cl, 0
    jg cycle

    pop DI
    pop SI
    pop CX
    pop AX
endm

; Clear List
clear_num_list macro list
    local l1
    push CX
    push SI

    mov SI, list            ; Set list pointer to SI
    mov CX, 0               ; Length 
    ; mov CL, byte ptr [SI+1] ;        of SI list
    mov CL, max_digits      ; CLEAR EVERYTHING

    mov byte ptr [SI], 0
    mov byte ptr [SI+1], 0
    add SI, 2
    l1:
        mov byte ptr [SI], placeholder
        inc SI
    loop l1
    
    pop SI
    pop CX
endm

; Copy the digits of list to DI
; Copy size and digits
; BUT NO SIGN
copy_num_list MACRO list
    local l1
    push AX
    push CX
    push SI
    push DI

    mov AX, 0               ; Buffer
    mov SI, list            ; Set list pointer to SI
    mov CX, 0               ; Length 
    mov CL, byte ptr [SI+1] ;        of SI list

    ; Start copying with length
    add SI, 1
    add DI, 1
    add CL, 1
    l1:
        mov AL, byte ptr [SI]
        mov byte ptr [DI], AL

        inc SI
        inc DI
    loop l1
    ; Copy system
    mov AL, byte ptr [SI]
    mov byte ptr [DI], AL

    pop DI
    pop SI
    pop CX
    pop AX
ENDM

; Copy list to di with sign
copy_num_full_list macro list
    push ax
    push si
    mov si, list
    mov ax, 0
    mov al, byte ptr [si]
    mov byte ptr [di], al
    copy_num_list list
    pop si
    pop ax
endm

; Add two num lists and set the result to DI
; Need num1_list and num2_list in stack
; Need result_list in DI
; Num lists should be in one system
; Corrupt regs
addition PROC
    locals @@
    push BP
    mov BP, SP

    mov ax, 0
    mov bx, 0
    mov cx, 0
    mov SI, word ptr [BP+6] ; num1_list ptr
    mov SI, word ptr [BP+4] ; num2_list ptr

    mov cx, 1
    set_digit_to_reg cx, ah, 1 ; Mov size of num1_list to ah
    mov cx, 2
    set_digit_to_reg cx, al, 1 ; Mov size of num2_list to al

    ; Set longer and shorter indexes
    cmp ah, al
    jl @@l1
        mov cs:longer, 1
        mov cs:shorter, 2
        jmp @@l2
    @@l1:
        mov cs:longer, 2
        mov cs:shorter, 1
    @@l2:

    ; Set shorter's offset
    set_digit_to_reg cs:longer, al, 1 
    set_digit_to_reg cs:shorter, ah, 1
    sub al, ah
    mov ah, 0
    mov cs:shorter_offset, ax

    ; Set result numeric system variable
    ; Like num1 list
    ; Num1 and num2 systems must be the same!
    set_digit_to_reg cs:longer, ah, max_digits+2
    mov cs:result_system, ah

    ; Set signs
    set_digit_to_reg cs:longer, ah, 0 
    set_digit_to_reg cs:shorter, al, 0
    ; Check if signes are the same
    xor ah, al
    cmp ah, 1
    je @@one_minus
    jmp @@same_sign
    @@one_minus:
        ; Subtraction

        ; Set sign to result
        set_digit_to_reg cs:longer, ah, 1 
        set_digit_to_reg cs:shorter, al, 1 
        ; Compare length
        cmp ah, al
        je @@length_equal
        jmp @@set_longer_sign
        @@length_equal:
            ; If length is equal
            ; Find the first greater digit
            mov cx, 0
            set_digit_to_reg cs:longer, cl, 1
            mov cs:counter, 2                   
            @@for_char:
                ; Load digits
                set_digit_to_reg cs:longer, ah, cs:counter
                set_digit_to_reg cs:shorter, al, cs:counter
                ; Compare them
                cmp ah, al
                je @@cmp_char_endif
                jl @@cmp_char_less
                @@cmp_char_greater:
                    ; If ah digit is greater
                    ; Set sign like longer
                    set_digit_to_reg cs:longer, ah, 0
                    mov byte ptr [DI], ah
                    jmp @@for_char_end
                @@cmp_char_less:
                    ; If ah digit is less
                    ; Set sign like shorter
                    set_digit_to_reg cs:shorter, al, 0
                    mov byte ptr [DI], al
                    ; Swap shorter and longer
                    ; Longer must be greater
                    mov ah, cs:longer
                    mov al, cs:shorter
                    mov cs:longer, al
                    mov cs:shorter, ah
                    jmp @@for_char_end
                @@cmp_char_endif:
                    ; If digits are equal increment
            inc cs:counter
            dec cx
            ; loop @@for_char
            cmp cl, 0
            jle @@for_char_end
            jmp @@for_char
            @@for_char_end:

            jmp @@end_sign
        @@set_longer_sign:
            ; If length is not equal
            ; Set longer sign as a result sign
            set_digit_to_reg cs:longer, ah, 0
            mov byte ptr [DI], ah
        @@end_sign:
        ; Now the correct sign is in the result
        
        ; Copy longer digits to result
        get_argument cs:longer  ; Set SI
        copy_num_list SI        ; Copy to DI
        reverse_num_list DI     ; Reverse DI
            
        ; Subtract shorter from reversed result
        ; Work with digits in DI
        add DI, 2
        ; Set number of iterations like shorter size
        mov cs:counter, 0   ; Counter
        mov cx, 0   ; Length of shorter
        set_digit_to_reg cs:shorter, cl, 1 
        @@subtract_cycle:
            ; Use DI digit as minuend
            ; Set shorter digit to al
            add cx, 1
            set_digit_to_reg cs:shorter, al, cx
            sub cx, 1
            ; Subtract and save to DI
            sub_byte cs:result_system
            
            inc cs:counter
            inc DI
        ; Make loop with far jump
        ; loop @@subtract_cycle
        dec cl
        cmp cl, 0
        jle @@subtract_cycle_end
        jmp @@subtract_cycle
        @@subtract_cycle_end:

        ; Reset DI
        sub DI, cs:counter
        mov cs:counter, 0
        mov ax, 0
        mov cx, 0
        set_digit_to_reg cs:longer, cl, 1

        ; Balance the system of DI
        ; Subtract zero
        @@subtract_cycle2:
            sub_byte cs:result_system
            inc DI
            inc cs:counter
        ; loop @@subtract_cycle2
        dec cx
        cmp cl, 0
        je @@subtract_cycle2_end
        jmp @@subtract_cycle2
        @@subtract_cycle2_end:

        ; Reset DI
        sub DI, cs:counter
        sub DI, 2
        reverse_num_list DI
        jmp @@end
    @@same_sign:
        ; Addition

        ; Work with digits in DI
        add DI, 2

        ; cs:counter is the length of result list
        ; In pure addition it is >= longer length
        mov cx, 0
        set_digit_to_reg cs:longer, cl, 1 
        mov cs:counter, cx

        ; Add shorter + part of longer to DI
        ; Set number of iterations like shorter size
        mov cx, 0
        set_digit_to_reg cs:shorter, cl, 1 
        @@addition_cycle:
            push CX
            ; Work with digits in num lists
            add cx, 2
            ; Fix numeration
            sub cx, 1
            ; Set longer digit to ah
            add cx, cs:shorter_offset
            set_digit_to_reg cs:longer, ah, cx 
            sub cx, cs:shorter_offset
            ; Set shorter digit to al
            set_digit_to_reg cs:shorter, al, cx
            ; Add them and save to result list
            add_byte cs:result_system

            pop CX
            inc DI
        ; Make loop with far jmp
        ; loop @@addition_cycle
        dec cx            
        cmp cx, 0
        je @@out_of_cycle
        jmp @@addition_cycle
        @@out_of_cycle:


        ; Add rest of longer to DI
        mov CX, cs:shorter_offset
        cmp CX, 0
        jle @@addition_cycle2_end
        mov AX, 0
        @@addition_cycle2:
            ; Set byte to ah
            push CX
            add CX, 2
            sub CX, 1
            set_digit_to_reg cs:longer, ah, cx 
            ; Save to result
            add_byte cs:result_system
            pop CX
            inc DI
        loop @@addition_cycle2
        @@addition_cycle2_end:

        
        ; If exceeded the longer length
        ; Increment result size
        cmp byte ptr [DI], placeholder
        je @@length_rslt_eq_lngr
            inc cs:counter
            inc DI
        @@length_rslt_eq_lngr:

        ; Restore DI
        sub DI, cs:counter
        sub DI, 2
        ; Update result list
        ; Set sign 
        set_digit_to_reg cs:longer, ah, 0 
        mov byte ptr [DI], ah
        ; Set size
        mov ax, cs:counter
        mov byte ptr [DI+1], al
        ; Set system like num1
        add DI, 2
        add DI, max_digits
        mov al, cs:result_system
        mov byte ptr [DI+1], al
        sub DI, max_digits
        sub DI, 2

        ; Reverse DI
        reverse_num_list DI
    @@end:
    mov SP, BP
    pop BP
    ret 4
longer db ?             ; Can be 1|2. Number of procedure argument. Reffers to offset
shorter db ?            ; Can be 1|2. Number of procedure argument. Reffers to offset
shorter_offset dw ?     ; Difference between longer and shorter lists
counter dw ?            ; Used as i in "for i" cycles
result_system db ?      ; Byte addition limit
addition ENDP


input_num_list MACRO list
    local cycle, exit
    cycle:
    ; Input string
    printMsg <&list&: >
    mov AH, 10
    lea DX, &list
    lea SI, &list
    mov byte ptr [SI], max_digits
	int 21h
    printBR
    ; Check input
    lea SI, &list
    call check_input
    pop AX
    ; Repeat if incorrect
    cmp AX, 0
    je exit
    jmp cycle
    exit:

ENDM

; SI+DI -> DI
num_lists_add MACRO
    ; Save regs
    push SI
    push DI

    push SI
    push DI

    ; Clear buffer
    lea DI, num_list_buff
    clear_num_list DI
    ; ADD old si to old di into buffer
    call addition
    ; Result is in buffer
    ; Set SI pointing to buffer
    mov SI, DI
    ; Restore old DI
    pop DI
    ; Copy buff to old DI 
    copy_num_full_list SI
    ; Restore SI
    pop SI
ENDM

; Push 1 if zero
; Push 0 if not zero
num_list_is_zero MACRO list
    local cycle, l1, l2, l3
    push CX
    push SI

    mov SI, list            ; Set list pointer to SI
    mov CX, 0               ; Length 
    mov CL, byte ptr [SI+1] ;        of SI list
    
    ; Check if every digit is zero
    add SI, 2
    cycle:
        ; If digit is zero?
        cmp byte ptr [SI], 0
        jne l2
        inc SI
    loop cycle
    
    
    l1: 
        ; Is zero 
        pop SI
        pop CX
        push 1
        jmp l3
    l2: 
        ; Is not zero
        pop SI
        pop CX
        push 0
        jmp l3
    l3: 
        ; Exit
    

ENDM

; Push list of max_digits size
; Breaks SI and CX
num_list_push macro list
    ; Fuck
endm

; Subtract 1 from list using num buffer
num_list_decrement macro list
    push SI
    push DI

    mov DI, list
    lea SI, num_list_minus1
    
    ; Copy list system to num_list_minus1
    push ax
    mov ah, byte ptr [2+di+max_digits-1]
    mov byte ptr [2+si+max_digits-1], ah
    pop ax
    ; -------------------------------------------------------------------------
    ; SIGN OF num_list_minus1 CORRUPTS AFTER num_lists_add
    ; LOOKS LIKE MEMORY LEAK
    ; PROBABLY ITERATE CYCLES +1 in addition proc
    ; TODO: 
    mov byte ptr [SI], 1
    ; -------------------------------------------------------------------------
    num_lists_add ; SI+DI -> DI
    pop DI
    pop SI
endm

DELAY MACRO duration
    local DELAY_LOOP
    MOV CX, duration
DELAY_LOOP:
    LOOP DELAY_LOOP
endm

printSIDI MACRO
   ; Print SI
    push si
    push di
    printMsg <SI: >
    call print_num_list
    printMSG < >
    pop di
    pop si
    
    ; Print DI
    push si
    push di
    printMsg <DI: >
    mov SI, DI
    call print_num_list
    printBR
    pop di
    pop si
    
ENDM
   

; Add num1_list num2_list times times to DI
; Need num1_list and num2_list in stack
; Need result_list in DI
; Num lists should be in one system
multiply proc
   locals @@
    push BP
    mov BP, SP


    mov ax, 0
    mov bx, 0
    mov cx, 0

    ; Work with signs
    mov SI, word ptr [BP+6] ; num1_list ptr
    mov cs:mult1, SI        ; Initialize cs:mult1
    mov AH, byte ptr [SI]   ; Set num1_list sign to AH
    mov SI, word ptr [BP+4] ; num2_list ptr
    mov cs:mult2, SI        ; Initialize cs:mult2
    mov AL, byte ptr [SI]   ; Set num2_list sign to AL

    ; Save arg signs
    push AX
    
    ; Calc sign of DI
    xor AH, AL
    mov cs:result_sign, AH
    
    ; Remove signs from args
    mov SI, cs:mult1
    mov byte ptr [SI], 0
    mov SI, cs:mult2
    mov byte ptr [SI], 0
    

    ; Check if cs:mult2 is zero
    num_list_is_zero cs:mult2
    pop AX
    cmp AX, 0
    je @@mult2_not_zero
    mov byte ptr [DI+1], 0
    jmp @@for_end
    @@mult2_not_zero:

    ; Copy mult1 to DI
    ; Like *1
    mov SI, cs:mult1
    copy_num_list cs:mult1
    num_list_decrement cs:mult2


    ; -------------------------------------------------------------------------
    ; SEE PROBLEM IN num_list_decrement macro 

    ; printMsg <------------------>
    ; num_lists_add ; clear buff; di=buff; call add (old si, old di);  copy buff -> di; 

    ; num_list_decrement cs:mult2
    ; num_list_decrement cs:mult2
    ; mov DI, cs:mult2
    ; jmp @@for_end
    ; -------------------------------------------------------------------------

    ; While num2_list != 0
    @@for_range:
    num_list_is_zero cs:mult2
    pop AX
    cmp AX, 0
    je @@for_body
    jmp @@for_end
    @@for_body:
        ; SI + DI -> DI
        ; mult1 + res to DI
        num_lists_add
        num_list_decrement cs:mult2
        ; delay 0FFFFh
    jmp @@for_range
    @@for_end:

    ; Set sign to DI
    mov AH, cs:result_sign
    mov byte ptr [DI], AH

    ; Restore signs to args
    pop AX
    mov SI, cs:mult1
    mov byte ptr [SI], AH
    mov SI, cs:mult2
    mov byte ptr [SI], AL

    mov SP, BP
    pop BP
    ret 4
mult1 dw ?          ; Pointer to 1 argument
mult2 dw ?          ; Pointer to 2 argument
result_sign db ?    ; Sign of DI
multiply endp


; Main
start:
    ; Load variables
    mov AX, data
    mov DS, AX
    mov AX, 0
    ; Code
    DEFINE_GET_STRING
    DEFINE_PRINT_STRING
    DEFINE_PRINT_NUM
    DEFINE_PRINT_NUM_UNS 
    ; Have a problem in decrement
    ; Have a problem in hex multiplication
    
    input_num_list num1_list
    input_num_list num2_list
    
    ; Example
    lea SI, num1_list
    printMSG <Num 1: >
    call print_num_list
    printBR
    push SI

    lea SI, num2_list
    printMSG <Num 2: >
    call print_num_list
    printBR
    push SI

    lea DI, result_list
    printMsg <+ operation>
    printBR
    call addition

    printMSG <Result: >
    mov SI, DI
    call print_num_list
    printBR

    
    lea SI, num1_list
    printMSG <Num 1: >
    call print_num_list
    printBR
    push SI

    lea SI, num2_list
    printMSG <Num 2: >
    call print_num_list
    printBR
    push SI
    
    printMsg <* operation>
    printBR
    call multiply

    printMSG <Result: >
    mov SI, DI
    call print_num_list

    exit:
    ; Out to DOS
    mov AH, 4Ch
    int 21h
code ends
end start 

