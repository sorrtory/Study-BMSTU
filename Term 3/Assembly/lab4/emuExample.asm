.MODEL SMALL
.STACK 100H

include emu8086.inc
; ORG    100h
.DATA
    msg1   DB  'Enter the number: ', 0


.CODE
    MAIN PROC
        MOV AX, @DATA       ; Initialize data segment
        MOV DS, AX



        LEA    SI, msg1       ; попросить ввести число
        CALL   print_string   ;
        CALL   scan_num       ; получить число в CX.

        MOV    AX, CX         ; копировать число в AX.

        ; напечатать следующие строки:
        CALL   pthis
        DB  13, 10, 'You have entered: ', 0

        CALL   print_num      ; напечатать число из AX.



        DEFINE_SCAN_NUM
        DEFINE_PRINT_STRING
        DEFINE_PRINT_NUM
        DEFINE_PRINT_NUM_UNS  ; требуется для print_num.
        DEFINE_PTHIS


        ; Exit program
        MOV AH, 4Ch
        INT 21h
    MAIN ENDP
END MAIN
