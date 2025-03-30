.MODEL SMALL
.STACK 100H

.DATA
    str1 DB 'Hello$', 0
    str2 DB 'World$', 0

.CODE
    MAIN PROC
        MOV AX, @DATA       ; Initialize data segment
        MOV DS, AX

        ; Push two parameters (string addresses) onto the stack
        LEA DX, str2        ; Load address of str2 into DX
        PUSH DX             ; Push str2 address onto stack

        LEA DX, str1        ; Load address of str1 into DX
        PUSH DX             ; Push str1 address onto stack

        ; Call the procedure to print both strings
        ; CALL PrintStrings

        ; Exit program
        MOV AH, 4Ch
        INT 21h
    MAIN ENDP

    ; Procedure to print two strings
    PrintStrings PROC
        PUSH BP             ; Save base pointer
        MOV BP, SP          ; Set BP to point to the current stack top
        
        ; Access the first parameter (str1) from the stack
        MOV DX, [BP+4]      ; First parameter is at [BP+4]
        MOV AH, 09h         ; Print string function (DOS interrupt)
        INT 21h

        ; Access the second parameter (str2) from the stack
        MOV DX, [BP+6]      ; Second parameter is at [BP+6]
        MOV AH, 09h         ; Print string function (DOS interrupt)
        INT 21h

        POP BP              ; Restore base pointer
        RET                 ; Return to caller
    PrintStrings ENDP
    ; Print linebreak
    printBR proc
        mov DL, 10
        mov AH, 02h
        int 21h
        ret
    printBR endp
END MAIN
