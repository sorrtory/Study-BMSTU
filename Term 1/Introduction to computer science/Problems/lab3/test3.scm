(define (ref xss . args)
  (define (list-head c x k)
    (if (zero? k)
        c
        (list-head (append c (cons (car x) '())) (cdr x) (- k 1))
        )
    )
  
  (if (= (length args) 1)
      ;; вывод
      (begin
        (cond ((list? xss)
               (and (> (length xss) (car args))
                    (list-ref xss (car args))))
              ((string? xss)
               (and (> (string-length xss) (car args))
                    (string-ref xss (car args))))
              ((vector? xss)
               (and (> (vector-length xss) (car args))
                    (vector-ref xss (car args))))
              (else #f)
              )
        )
        
      ;;вставка
      (begin
        (cond ((list? xss)
               (and (>= (length xss) (car args))
                    (append (list-head '() xss (car args)) (cons (cadr args) '()) (list-tail xss (car args)))))
              ((string? xss)
               (and (and (>= (string-length xss) (car args)) (char? (cadr args)))
                    (list->string (append (list-head '() (string->list xss) (car args)) (cons (cadr args) '()) (list-tail (string->list xss) (car args))))))
              ((vector? xss)
               (and (>= (vector-length xss) (car args))
                    (list->vector (append (list-head '() (vector->list xss) (car args)) (cons (cadr args) '()) (list-tail (vector->list xss) (car args))))))
              (else #f)
              )
        
        )
      )
  )
  
(ref '(1 2 3) 1) ;; ⇒ 2
(ref #(1 2 3) 1) ;; ⇒ 2
(ref "123" 1)    ;; ⇒ #\2
(ref "123" 3)    ;; ⇒ #f

(newline)

(ref '(1 2 3) 1 0)   ;; ⇒ (1 0 2 3)
(ref #(1 2 3) 1 0)   ;; ⇒ #(1 0 2 3)
(ref #(1 2 3) 1 #\0) ;; ⇒ #(1 #\0 2 3)
(ref "123" 1 #\0)    ;; ⇒ "1023"
(ref "123" 1 0)      ;; ⇒ #f
(ref "123" 3 #\4)    ;; ⇒ "1234"
(ref "123" 5 #\4)    ;; ⇒ #f

