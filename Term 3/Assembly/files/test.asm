assume CS:code, DS:data

data segment
    hello db 1
    output_buffer db "????$"   ; Buffer for output, large enough to hold the number and the end character
data ends

code segment
start:
    ; mov ax, data
    ; mov 
    mov ax, 1
    

convert_to_decimal:
    mov di, offset output_buffer + 4 ; Set DI to point to the end of the buffer (after the '$')
    mov cx, 10                       ; Set the divisor to 10 (decimal)
    
decimal_loop:
    xor dx, dx                       ; Clear DX (DX:AX pair used in division)
    div cx                           ; Divide AX by 10, quotient in AX, remainder in DX
    add dl, 30h                      ; Convert remainder to ASCII character (0-9)
    dec di                           ; Move back to the next character position in the buffer
    mov [di], dl                     ; Store ASCII character in buffer

    test ax, ax                      ; Check if AX (quotient) is zero
    jnz decimal_loop                 ; If not zero, continue dividing

exit:
    mov ah, 09h                      ; DOS function to print string
    mov dx, di                       ; Set DX to point to the start of the number in the buffer
    int 21h                          ; Call DOS interrupt to display the number
    ; mov AH, 4Ch


code ends
end start
