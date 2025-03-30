 
; TASM:
; TASM /m PM.asm
; TLINK /x /3 PM.obj
; PM.exe
 
; MASM:
; ML /c PM.asm
; LINK PM.obj,,NUL,,,
; PM.exe
 
        .386p                                           ; разрешить привилегированные инструкции i386
       
; СЕГМЕНТ КОДА (для Real Mode)

; Print message
printMsg macro startAddr, msg, line
    push ax
    push bx
    push cx
    push dx
    push si
    push di

    xor EAX, EAX
    mov AX, 0A0h 
    mov BL, line
    mul BL
    mov EDI, startAddr
    add EDI, EAX

    mov AH, 01h
    add AH, line
    ; if line gt 13
    ;     sub AH, 10
    ; endif
    irpc char, <msg>
        mov al, '&char'
        mov word ptr [EDI], ax
        add EDI, 2
    endm

    pop di
    pop si
    pop dx
    pop cx
    pop bx
    pop ax
endm

; Print bit
print16 macro startAddr, data, line
    local l1, l2, l3, l4
    push eax
    push ebx
    push ecx
    push edx
    push esi
    push edi

    xor EAX, EAX
    mov AX, 0A0h 
    mov BL, line
    mul BL
    mov EDI, startAddr
    add EDI, EAX ; Set line to EDI
    mov ESI, EDI

    ; Set line color to bh
    mov BH, 01h
    add BH, line
    ; if line gt 13
    ;     sub BH, 10 
    ; endif
    

    ; Print 
    mov al, data
    len=2
    mov cx, len

    l3:
        xor AH, AH
        mov BL, 16
        div BL
        ; Print remainder
            cmp ah, 10
            jl l1
            sub ah, 10
            add ah, 'A'
            jmp l2
            l1:
            add ah, '0'
            l2:    
            mov BL, AH
            mov word ptr [EDI], BX
            add EDI, 2
            ; inc CX
        ; cmp AL, 0
        ; jne l3
    loop l3
    
    mov ax, len
    mov bl, 2
    div bl
    mov cx, 0
    mov cl, al
    sub EDI, 2
    l4:
        mov AX, word ptr [ESI]
        mov BX, word ptr [EDI]
        mov word ptr [ESI], BX
        mov word ptr [EDI], AX
        add ESI, 2
        sub EDI, 2
    loop l4

    pop edi
    pop esi
    pop edx
    pop ecx
    pop ebx
    pop eax
    add edi, 4
endm

; ----------------------------------------------------------------------------------
RM_CODE segment     para public 'CODE' use16
                   assume CS:RM_CODE,SS:RM_STACK
                ;    include emu8086.inc
@@start:
                   mov    AX,03h
                   int    10h                                                  ; текстовый режим 80x25 + очистка экрана
        ; открываем линию А20 (для 32-х битной адресации):
                   in     AL,92h
                   or     AL,2
                   out    92h,AL
 
        ; вычисляем линейный адрес метки ENTRY_POINT (точка входа в защищенный режим):
                   xor    EAX,EAX                                              ; обнуляем регистра EAX
                   mov    AX,PM_CODE                                           ; AX = номер сегмента PM_CODE
                   shl    EAX,4                                                ; EAX = линейный адрес PM_CODE
                   add    EAX,offset ENTRY_POINT                               ; EAX = линейный адрес ENTRY_POINT
                   mov    dword ptr ENTRY_OFF,EAX                              ; сохраняем его в переменной
        ; (кстати, подобный "трюк" называется SMC или Self Modyfing Code - самомодифицирующийся код)
        ; теперь надо вычислить линейный адрес GDT (для загрузки регистра GDTR):
                   xor    EAX,EAX
                   mov    AX,RM_CODE                                           ; AX = номер сегмента RM_CODE
                   shl    EAX,4                                                ; EAX = линейный адрес RM_CODE
                   add    AX,offset GDT                                        ; теперь EAX = линейный адрес GDT
 
        ; линейный адрес GDT кладем в заранее подготовленную переменную:
                   mov    dword ptr GDTR+2,EAX
        ; а подобный трюк назвать SMC уже нельзя, потому как по сути мы модифицируем данные <img src="styles/smiles_s/smile3.gif" class="mceSmilie" alt=":smile3:" title="Smile3    :smile3:">
 
        ; собственно, загрузка регистра GDTR:
                   lgdt   fword ptr GDTR
 
        ; запрет маскируемых прерываний:
                   cli
        
        ; запрет немаскируемых прерываний:
                   in     AL,70h
                   or     AL,80h
                   out    70h,AL
 
        ; переключение в защищенный режим:
                   mov    EAX,CR0
                   or     AL,1
                   mov    CR0,EAX
 
        ; загрузить новый селектор в регистр CS
                   db     66h                                                  ; префикс изменения разрядности операнда
                   db     0EAh                                                 ; опкод команды JMP FAR
        ENTRY_OFF  dd     ?                                                    ; 32-битное смещение
                   dw     00001000b                                            ; селектор первого дескриптора (CODE_descr)
 
        ; ТАБЛИЦА ГЛОБАЛЬНЫХ ДЕСКРИПТОРОВ:
        GDT:       
        ; нулевой дескриптор (обязательно должен присутствовать в GDT!):
        NULL_descr db     8 dup(0)
        
        CODE_descr db     0FFh,0FFh,00h,00h,00h,10011011b,11001111b,00h
        DATA_descr db     0FFh,0FFh,00h,00h,00h,10010010b,11001111b,00h
        Stack_descr db    0FFh,0FFh,00h,00h,02h,10010010b,11001111b,00h
        VIDEO_descr db     0FFh,0FFh,00h,80h,0Bh,10010010b,01000000b,0CCh  ; Video: Base 0x000B8000
        
        ; 64 bits

        ; 16 bits limit         0xFFFF
        ; 24 bits base          0x000000
        ; 8 bit type flags      10011010b (code) / 10010010b (data)
        ; 8 bit Flags and stack 11001111b
        ; 16 bit Base           0x00
        
        ; Extra segms
        Data2_descr db    0FFh,0FFh,00h,00h,06h,10011110b,11001111b,00h
        COD2_descr db     0F2h,01Fh,00h,00h,08h,11111101b,11001111b,00h
        Broken_descr db    0F1h,0FFh,00h,00h,04h,01000000b,0FFh,00h

        GDT_size   equ    $-GDT                                                ; размер GDT
 
        GDTR       dw     GDT_size-1                                           ; 16-битный лимит GDT
                   dd     ?                                                    ; здесь будет 32-битный линейный адрес GDT
RM_CODE ends
; -----------------------------------------------------------------------------
 
 
 
; СЕГМЕНТ СТЕКА (для Real Mode)
; -----------------------------------------------------------------------------
RM_STACK segment          para stack 'STACK' use16
                 db 100h dup(?)        ; 256 байт под стек - это даже много
RM_STACK ends
; -----------------------------------------------------------------------------
 

; СЕГМЕНТ КОДА (для Protected Mode)
; -----------------------------------------------------------------------------
PM_CODE segment     para public 'CODE' use32
                        assume CS:PM_CODE,DS:PM_DATA
        ENTRY_POINT:    
        ; загрузим сегментные регистры селекторами на соответствующие дескрипторы:
                        mov    AX,00010000b                   ; селектор на второй дескриптор (DATA_descr)
                        mov    DS,AX                          ; в DS его
                        mov    ES,AX                          ; его же - в ES
                        mov AX, 00011000b
                        mov SS, AX
                        mov esp, 0002FFFFFh

 
        ; * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
        ; создать каталог страниц
                        mov    EDI,00100000h                  ; его физический адрес - 1 Мб
                        mov    EAX,00101007h                  ; адрес таблицы 0 = 1 Мб + 4 Кб
                        stosd                                 ; записать первый элемент каталога
                        mov    ECX,1023                       ; остальные элементы каталога -
                        xor    EAX,EAX                        ; нули
                        rep    stosd
        ; заполнить таблицу страниц 0
                        mov    EAX,00000007h                  ; 0 - адрес страницы 0
                        mov    ECX,1024                       ; число страниц в таблице
        fill_page_table:
                        stosd                                 ; записать элемент таблицы
                        add    EAX,00001000h                  ; добавить к адресу 4096 байтов
                        loop   fill_page_table                ; и повторить для всех элементов
        ; поместить адрес каталога страниц в CR3
                        mov    EAX,00100000h                  ; базовый адрес = 1 Мб
                        mov    CR3,EAX
        ; включить страничную адресацию,
                        mov    EAX,CR0
                        or     EAX,80000000h
                        mov    CR0,EAX
        ; а теперь изменить физический адрес страницы 12000h на 0B8000h
                        mov    EAX,000B8007h
                        mov    ES:00101000h+012h*4,EAX
        
        ; Scan GDT
        mov    ESI,PM_DATA
        shl    ESI,4
        add ESI, offset gdt2
        sgdt [esi]

        printMsg 012000h, <N   Limit        Base      Type Direc Edit    Access S   DPL  P   AVL  D/B>, 0

        mov ax, word ptr [esi + 2] ; Load GDT base address (low part)
        mov dx, word ptr [esi + 4] ; Load GDT base address (high part)
        shl dx, 16
        add ax, dx                   ; Full GDT base address in AX

        mov cx, word ptr [esi] ; Load GDT limit
        shr cx, 3                    ; Divide limit by 8 (number of descriptors)
        
        mov ch, 1                   ; Start with 1 line
        mov bx, 8                   ; Skip 0 descriptor
        .l11:
            mov si, ax               ; GDT base address
            add si, bx               ; Descriptor address (Base + Index * 8)

            
            mov edi, 012000h
            ; Number
            print16 edi, ch, ch 

            ; Check O
            mov dl, byte ptr [si+6]
            shr dl, 5
            and dl, 01h

            cmp dl, 1
            jne .l14
            add edi, 4
            printMsg edi, <BROKEN>, ch
            ; print16 edi, dl, ch 
            jmp .l13
            .l14:
            ; Limit
            add edi, 4
            ; High
            mov dl, byte ptr [si+6]
            and dl, 0fh
            print16 edi, dl, ch 
            ; Low
            mov dx, word ptr [si]             
            print16 edi, dh, ch 
            print16 edi, dl, ch
            ; G
            mov dl, byte ptr [si+6]
            shr dl, 7
            and dl, 01h
            print16 edi, dl, ch 
            cmp dl, 1
            je .l112
            printMSG edi, <xB>, ch             
            jmp .l111
            .l112:
            printMSG edi, <x4KB>, ch 
            .l111:

            ; Base
            add edi, 10
            ; High
            mov dl, byte ptr [si+7]            
            print16 edi, dl, ch
            ; Mid
            mov dl, byte ptr [si+4]            
            print16 edi, dl, ch
            ; Low
            mov dx, word ptr [si+2]
            print16 edi, dh, ch 
            print16 edi, dl, ch

            ; Type
            add edi, 4
            mov dl, byte ptr [si+5]
            and dl, 01h
            ; Executable
            cmp dl, 1
            je .l1Ex
            printMSG edi, <DATA>, ch
            mov dh, 0
            jmp .l1En
            .l1Ex:
            printMSG edi, <CODE>, ch
            mov dh, 1
            .l1En:
            add edi, 8

            ; Direction
            add edi, 2
            mov dl, byte ptr [si+5]
            shr dl, 1
            and dl, 01h
            cmp dl, 1
            je .l2Ex
                cmp dh, 1
                je .l2Code
                printMSG edi, <UP>, ch
                jmp .l2InE
                .l2Code:
                printMSG edi, <NCONF>, ch
                .l2InE:
            jmp .l2En
            .l2Ex:
                cmp dh, 1
                je .l2Code1
                printMSG edi, <DN>, ch
                jmp .l2InE1
                .l2Code1:
                printMSG edi, <CONF>, ch
                .l2InE1:
            .l2En:
            add edi, 10

            ; Writable
            add edi, 2
            mov dl, byte ptr [si+5]
            shr dl, 2
            and dl, 01h
            cmp dl, 1
            je .l3Ex
                cmp dh, 1
                je .l3Code
                printMSG edi, <NWRITE>, ch
                jmp .l3InE
                .l3Code:
                printMSG edi, <NREAD>, ch
                .l3InE:
            jmp .l3En
            .l3Ex:
                cmp dh, 1
                je .l3Code1
                printMSG edi, <DOWRITE>, ch
                jmp .l3InE1
                .l3Code1:
                printMSG edi, <DOREAD>, ch
                .l3InE1:
            .l3En:

            ; Accessed
            add edi, 16 
            mov dl, byte ptr [si+5]
            shr dl, 3
            and dl, 01h
            print16 edi, dl, ch 


            ; S
            add edi, 10
            mov dl, byte ptr [si+5]
            shr dl, 4
            and dl, 01h
            print16 edi, dl, ch 
            ; DPL
            add edi, 4
            mov dl, byte ptr [si+5]
            shr dl, 5
            and dl, 03h
            print16 edi, dl, ch 
            ; Present
            add edi, 6
            mov dl, byte ptr [si+5]
            shr dl, 7
            and dl, 01h
            print16 edi, dl, ch 
            ; AVL
            add edi, 4
            mov dl, byte ptr [si+6]
            shr dl, 4
            and dl, 01h
            print16 edi, dl, ch 
            ; D/B
            add edi, 6
            mov dl, byte ptr [si+6]
            shr dl, 6
            and dl, 01h
            print16 edi, dl, ch 


            add bx, 8                ; Move to the next descriptor
        ; loop .l11               ; Repeat for all descriptors
        .l13:
        inc ch
        dec cl
        cmp cl, 0
        je .l12
        jmp .l11
        .l12:
                        jmp    $                              ; погружаемся в вечный цикл
PM_CODE ends
; -------------------------------------------------------------------------------------
 
 
; СЕГМЕНТ ДАННЫХ (для Protected Mode)
; -------------------------------------------------------------------------------------
PM_DATA segment        para public 'DATA' use32
                assume CS:PM_DATA       
        
        mes_len equ    66

        gdt2    dw ?
                dd ?
                
PM_DATA ends
; ----------------------------------------------------------------------------------------------  
                end         @@start