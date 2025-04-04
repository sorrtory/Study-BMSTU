; td for debugger. Alt+x to exit

assume CS:code, DS:data
; 8 * a / b + (c + d) / 2
data segment
    a db 10
    b db 1
    c db 1
    d db 1

    frac1 dw ?
    frac2 dw ?
    res dw ?

    str10 db ?, ?, ?, '$'
    str16 db ?, ?, ?, '$'

data ends

code segment
start:
    mov AX, data
    mov DS, AX
    mov AH, 0

    ; 8*a
    mov AL, a
    shl AL, 3

    ; / b
    mov BL, b  
    div BL    

    mov frac1, AX

    mov AL, c
    mov BL, d

    ; c+d
    add AL, BL

    ; /2
    shr AL, 1

    mov frac2, AX

    ; frac1+frac2
    mov AX, frac1
    mov BX, frac2

    add AX, BX

    mov res, ax

    ;;;; OUTPUT
    jmp go_10

d_loop:
    ; ; pick
    xor dx, dx                      
    div cx                            
    add dl, 30h    
    ; ; next                  
    ; mov ax, res
    mov str10[bx], dl
    inc bx     
    ; mov ah, 0
    ; mov ax, res1
    ; if ax == 0              
    cmp ax, 0
    jz  print_10              
    jnz d_loop
    ; jmp print_10  

h_loop:
    ; pick
    xor dx, dx                      
    div cx                            

    ; ASCII check
    cmp dx, 10
    jg _else
    then:
        add dl, 30h
        jmp _endif
    _else:
        add dl, 41h
    _endif:

            
    ; next                  
    dec di                           
    mov [di], dl
    ; if ax == 0              
    cmp ax, 0
    jz  print_16            
    jnz h_loop  

go_10:
    mov ax, res
    ; array?
    xor bx, bx
    
    ; mov si, offset str10 ; Зачем офсет?
    ; lea di, str10
    ; divider
    mov cx, 10

    jmp d_loop

go_16:
    xor ax, ax
    xor bx, bx
    xor cx, cx
    xor dx, dx
    ; xor ax, ax
    ; xor ax, ax
    ; xor ax, ax
    ; xor ax, ax
    ; xor di, di


    mov ax, res
    ; array?
    mov di, offset str16 ; Зачем офсет,
    ; divider
    mov cx, 16

    jmp h_loop

print_10:
    mov AH, 09h
    mov DX, DI
    int 21h

    jmp go_16

print_16:
    ; newline
    MOV dl, 10
    MOV ah, 02h
    INT 21h
    ; ; carriage return
    ; MOV dl, 13
    ; MOV ah, 02h
    ; INT 21h

    mov AH, 09h
    mov DX, DI
    int 21h

    jmp exit

exit:
    mov AH,4Ch
    int 21h



code ends
end start