;; <Program>  ::= <Articles> <Body> .
;; <Articles> ::= <Article> <Articles> | .
;; <Article>  ::= define word <Body> end .
;; <Body>     ::= if <Body> endif <Body> | integer <Body> | word <Body> | .


;; TODO: word!= специальные слова типа define if 
(define EOF (integer->char 1))

;; Конструктор потока
(define (make-stream items . eos)
  (if (null? eos)
      (make-stream items #f)
      (list (vector->list items) (car eos))))

;; Запрос текущего символа
(define (peek stream)
  (if (null? (car stream))
      (cadr stream)
      (caar stream)))

;; Запрос первых двух символов
(define (peek2 stream)
  (if (null? (car stream))
      (cadr stream)
      (if (null? (cdar stream))
          (list (caar stream))
          (list (caar stream) (cadar stream)))))

;; Продвижение вперёд
(define (next stream)
  (let ((n (peek stream)))
    (if (not (null? (car stream)))
        (set-car! stream (cdr (car stream))))
    n))




(define (parse tokens)
  (define stream (make-stream tokens EOF))
  (call-with-current-continuation
   (lambda (stack)
       (Program stream stack))))


;; <Program>  ::= <Articles> <Body> .
(define (Program stream stack)
  (define out (cons (Articles stream stack) (cons (Body stream stack) '())))
  out)


;; <Articles> ::= <Article> <Articles> | .
(define (Articles stream stack)
  (cond
    ((equal? (peek stream) 'define)
     (cons (Article stream stack) (Articles stream stack)))
    (else '())))
  
;; <Article>  ::= define word <Body> end .
(define (Article stream stack)
  (next stream)  ; съедаем 'define
  (let* ((word (next stream)) 
         (body (Body stream stack)))
  
    (if (and (equal? (peek stream) 'end) (not (member word '(if define end endif))))
        (begin (next stream) (cons word (cons body '())))
        (stack #f))))

;; <Body>     ::= if <Body> endif <Body> | integer <Body> | word <Body> | .
(define (Body stream stack)
  (cond
    ((equal? (peek stream) 'if)
     (next stream)  ; съедаем 'if
     (let ((ifbody (cons 'if (cons (Body stream stack) '()))))
       (if (equal? (peek stream) 'endif)
           (begin  (next stream) (cons ifbody (Body stream stack)))
           (stack #f))))
    
    ((number? (peek stream))
     (let ((intgr (next stream))) ; съедаем integer
       (cons intgr (Body stream stack))))
    
    ((and (symbol? (peek stream)) (not (member (peek stream) '(endif end define))))
    (let ((word (peek stream))) ; съедаем word
      (next stream)
      (cons word (Body stream stack))))
    (else '())))


;; Тесты

(parse #(1 2 +)) ;; ⇒ (() (1 2 +))
(newline)

(parse #(x dup 0 swap if drop -1 endif))
    ;; ⇒ (() (x dup 0 swap (if (drop -1))))
(newline)

(parse #( define -- 1 - end
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
          4 factorial ))
#|
 ⇒
 (((-- (1 -))
   (=0? (dup 0 =))
   (=1? (dup 1 =))
   (factorial
    (=0? (if (drop 1 exit)) =1? (if (drop 1 exit)) dup -- factorial *)))
  (0 factorial 1 factorial 2 factorial 3 factorial 4 factorial))
|#
(newline)

(parse #(define word w1 w2 w3)) ;; ⇒ #f
(newline)


;; Доп тесты

(parse #(0 if 1 if 2 endif 3 endif 4))
(newline)

(parse #(1 if 2 if 3 endif 4 endif 5))
(newline)

(parse #(   define =0? dup 0 = end
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
                10 make-fib     ))
(newline)

(parse #(123 if end))
(newline)

(parse #(end 123))
(newline)

(parse #(if define end endif))
(newline)
