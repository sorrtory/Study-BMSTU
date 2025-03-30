.MODEL SMALL
.STACK 100H

.DATA
    myString DB 'hello', 0   ; Null-terminated string

.CODE
    MAIN PROC
        MOV AX, @DATA                ; Initialize data segment
        MOV DS, AX

        LEA SI, myString             ; Load address of the string into SI
        CALL GetLength               ; Call procedure to get length

        ; After return, length will be in CX register
        
        ; Exit program
        MOV AH, 4Ch
        INT 21h
    MAIN ENDP

    ; Procedure to get length of null-terminated string
    GetLength PROC
        XOR CX, CX                   ; Clear CX, used to store length

    NextChar:
        MOV AL, [SI]                 ; Load character from string
        CMP AL, 0                    ; Check if it is the null terminator (00h)
        JE Done                      ; If it is, we're done

        INC CX                       ; Increment length count
        INC SI                       ; Move to the next character
        JMP NextChar                 ; Repeat until terminator is found

    Done:
        RET                          ; Return, length in CX
    GetLength ENDP

END MAIN
