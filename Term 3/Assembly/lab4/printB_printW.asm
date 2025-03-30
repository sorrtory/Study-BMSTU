.MODEL SMALL
.STACK 100h


.DATA
    digit db 5              ; A sample digit stored in the data segment
    num db 52           ; A sample digit stored in the data segment
    numw dw 122           ; A sample digit stored in the data segment

.CODE
    ; Macro to print a digit from the data segment
    PRINT_DIGIT MACRO offset
        mov ah, 02h          ; DOS interrupt to print a character in DL
        mov al, [offset]     ; Load the digit from the data segment into AL
        add al, '0'          ; Convert the digit to ASCII (add ASCII code for '0')
        mov dl, al           ; Move ASCII character to DL for printing
        int 21h              ; Call DOS interrupt to print the character
    ENDM

    ; Print message
    printMsg macro msg
        irpc char, <msg>
            mov dl, '&char'
            mov AH, 02h
            int 21h
        endm
    endm

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

    PRINT_WORD_10 macro num
        local print, cycle

        mov cx, 0
        mov ax, num
        mov bx, 10

        cycle:
            mov dx, 0 
            cmp ax, 0
            je print
        
            div bx ; al=ax/10 ; ah=remainder
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

print_10 macro num
    if type num eq 1
        PRINT_BYTE_10 num
    elseif type num eq 2
        PRINT_WORD_10 num
    else
        printMsg <Can't print this type>
    endif
endm

MAIN PROC
    mov ax, @data            ; Initialize data segment
    mov ds, ax

    ; PRINT_BYTE_10 num
    ; PRINT_WORD_10 numw
    print_10 num
 
    
    ; Exit program
    mov ax, 4C00h            ; DOS function to terminate program
    int 21h
MAIN ENDP
END MAIN
