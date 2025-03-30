.MODEL SMALL
.STACK 100h

.DATA
    msg db "Byte value: $"

.CODE
main:
    MOV AX, @data      ; Initialize data segment
    MOV DS, AX

    ; Example of a negative byte
    MOV AL, -50        ; AL = -50, signed byte

    ; Print the message "Byte value: "
    MOV DX, offset msg
    CALL PrintString

    ; Check if the byte is negative
    TEST AL, 80h       ; Test if the highest bit (sign bit) is set
    JZ PrintPositive   ; If AL is positive or zero, jump to PrintPositive

    ; If AL is negative, print a minus sign
    MOV DL, '-'        ; Load minus sign in DL
    CALL PrintChar

    ; Convert the negative value to positive for printing
    NEG AL             ; AL = -50 becomes 50
PrintPositive:
    ; Print the positive value of AL (50)
    CALL PrintByte

    ; End program
    MOV AH, 4Ch
    INT 21h

; Function to print a string (terminated with $)
PrintString:
    MOV AH, 09h
    INT 21h
    RET

; Function to print a byte value in AL
PrintByte:
    ADD AL, '0'        ; Convert byte to ASCII
    MOV DL, AL         ; Move the ASCII character to DL
    CALL PrintChar
    RET

; Function to print a single character in DL
PrintChar:
    MOV AH, 02h
    INT 21h
    RET

END main
