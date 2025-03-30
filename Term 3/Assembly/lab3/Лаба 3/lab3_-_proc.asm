assume cs: code, ds: data

data segment
vara db 1
string db 100, 99 dup (0)
data ends

code segment
print proc
	push bp
	mov bp, sp
	
	mov dx, [bp+4]
	mov ah, 09h
	int 21h
	pop bp
	pop bx
	xor ax, ax
	push ax
	push bx
	ret
print endp


start:	mov ax, data
		mov ds, ax
		mov dx, offset string
		mov ax, 0
		mov ah, 0Ah
		int 21h
		
		push dx
		call print
		
		pop dx
		cmp dx, 0
		jne start

		mov ah, 4ch
		int 21h
		code ends
		end start