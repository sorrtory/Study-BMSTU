(define (interpret program stack)

    (define (<> a b) (not (= a b))) ;; Не равно
    (define (bool->integer b) (case b ((#f) 0) ((#t) -1))) ;; Функция перевода из бул в местный инт
    (define lp (vector-length program)) ;; Длина программы
    (let loop ((i 0) (vars '()) (stack stack) (backs '()))
      (if (>= i lp)
          stack
          (let ((WORD (vector-ref program i)))
            (cond
              ;; Цифры
              ((number? WORD) (loop (+ i 1) vars (append `(,WORD) stack) backs))
              
              ;; Арифметические операции (WORD (cadr stack) (car stack)) remainder
              ((member WORD `(+ * -))
               (loop (+ i 1) vars (append `(,(eval `(,WORD ,(cadr stack)
              ,(car stack)) (interaction-environment))) (cddr stack)) backs))
              ((member WORD `(/))
               (loop (+ i 1) vars (append `(,(eval `(quotient ,(cadr stack)
              ,(car stack)) (interaction-environment))) (cddr stack) backs)))
              ((member WORD `(mod))
               (loop (+ i 1) vars (append `(,(eval `(remainder ,(cadr stack)
              ,(car stack)) (interaction-environment))) (cddr stack)) backs))
              ((member WORD `(neg)) (loop (+ i 1) vars (append `(,(eval `(- ,(car stack))
                                         (interaction-environment))) (cdr stack)) backs))
              
              ;; Операции сравнения
              ((member WORD `(= > <))
               (loop (+ i 1) vars (cons (bool->integer (eval `(,WORD ,(cadr stack)
              ,(car stack)) (interaction-environment))) (cddr stack)) backs))
              
              ;; Логические операции
              ((member WORD `(and or))
               (loop (+ i 1) vars (cons (bool->integer (eval `(,WORD ,(<> (car stack)
              0) ,(<> (cadr stack) 0)) (interaction-environment))) (cddr stack)) backs))
              ((member WORD `(not)
              ) (loop (+ i 1) vars (cons (bool->integer (eval `(,WORD ,(<> (car stack)
              0)) (interaction-environment))) (cdr stack)) backs))
              
              ;; Операции со стеком
              ((member WORD `(drop)) (loop (+ i 1) vars (cdr stack) backs))
              ((member WORD `(swap))
               (loop (+ i 1) vars (append `(,(cadr stack)) `(,(car stack)) (cddr stack)) backs))
              ((member WORD `(dup))
               (loop (+ i 1) vars (append `(,(car stack)) `(,(car stack)) (cdr stack)) backs))
              ((member WORD `(over))
               (loop (+ i 1) vars (cons (list-ref stack 1) stack) backs))
              ((member WORD `(rot)) (loop (+ i 1) vars (append `(,(caddr stack))
                                       `(,(cadr stack)) `(,(car stack)) (cdddr stack) backs)))
              ((member WORD `(depth)) (loop (+ i 1) vars (cons (length stack) stack) backs))
              
              ;; Управляющие конструкции
              
              ((member WORD `(define))
               (let defloop ((i (+ i 2))
                             (vars vars) (stack stack) (define_name (vector-ref program (+ i 1)))
               (defWORD (vector-ref program (+ i 2))) (defIndex (+ i 2)))
                 (if (equal? defWORD 'end)
                     (loop (+ i 1)
                     (append vars (list (cons define_name (cons defIndex '())))) stack backs)
                     (defloop (+ i 1)
                     vars stack define_name (vector-ref program (+ i 1)) defIndex))))
            
              ((member WORD `(exit end))
               (if (<> (length backs) 0)
                   (loop (car backs) vars stack (cdr backs))))
            
              ((member WORD `(if))
               (let ifloop ((i (+ i 1)) (vars vars) (stack (cdr stack))
                 (flag (car stack)) (ifWORD (vector-ref program (+ i 1))) (ifIndex (+ i 1)))  
                 (if (equal? ifWORD 'endif)
                     (if (= flag 0)
                         (loop (+ i 1) vars stack backs)
                         (loop ifIndex vars stack backs))
                     (ifloop (+ i 1)
                     vars stack flag (vector-ref program (+ i 1)) ifIndex))))
            
              ((member WORD `(endif)) (loop (+ i 1) vars stack backs))                         
            (else
             (loop (cadr (assoc WORD vars)) vars stack (cons (+ i 1) backs))))))))
;; Тестирование
(load "/home/z/scheme_fan/lab3/unit-test.scm")

(define the-tests
  (list

   (test (interpret #(   define abs
                          dup 0 <
                          if neg endif
                          end
                          9 abs
                          -9 abs      ) (quote ())) '(9 9))
   (test (interpret #(   define =0? dup 0 = end
                          define <0? dup 0 < end
                          define signum
                          =0? if exit endif
                          <0? if drop -1 exit endif
                          drop
                          1
                          end
                          0 signum
                          -5 signum
                          10 signum       ) (quote ()))  '(1 -1 0))
   (test (interpret #(   define -- 1 - end
                          define =0? dup 0 = end
                          define =1? dup 1 = end
                          define factorial
                          =0? if drop 1 exit endif
                          =1? if drop 1 exit endif
                          dup --
                          factorial
                          *
                          end
                          0 factorial
                          1 factorial
                          2 factorial
                          3 factorial
                          4 factorial     ) (quote ()))  '(24 6 2 1 1))
   (test (interpret #(   define =0? dup 0 = end
                          define =1? dup 1 = end
                          define -- 1 - end
                          define fib
                          =0? if drop 0 exit endif
                          =1? if drop 1 exit endif
                          -- dup
                          -- fib
                          swap fib
                          +
                          end
                          define make-fib
                          dup 0 < if drop exit endif
                          dup fib
                          swap --
                          make-fib
                          end
                          10 make-fib     )
                          (quote ()))  '(0 1 1 2 3 5 8 13 21 34 55))
   (test (interpret #(   define =0? dup 0 = end
                          define gcd
                          =0? if drop exit endif
                          swap over mod
                          gcd
                          end
                          90 99 gcd
                          234 8100 gcd    ) '())  '(18 9))    ))

(run-tests the-tests)


