;; L(1)
;; <Поток> ::= <Выражение> | #f
;; <Выражение> ::= <Пробел> | <Дробь> | <Пробел> <Выражение> | <Выражение> <Пробел>
;; <Знак> ::= ε | -
;; <Дробь> ::= <Знак> <Цифорки> / <Цифорки>
;; <Пробел> ::= \tab | \newline | \space | ε
;; <Цифорки> ::= ЧИСЛО

(define (sign? x)
  (or (equal? x #\-) (equal? x #\+)))

(define (minus_or_nothing x stream)
  (if (sign? x)
      (begin (next stream) (if (equal? x #\+) '() '(-)))
      '()
      )
  )

(define (slash? x)
  (equal? x #\/)
  )

;; Конструктор потока
(define (make-stream items . eos)
  (if (null? eos)
      (make-stream items #f)
      (list (string->list items) (car eos))))

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


(define (check-frac xs)
  
  (define stream (make-stream xs))
  #f ;; А почему если это убрать, то ничего не работает? Потому что letrec!
  (define error #f)
  (define X (minus_or_nothing (peek stream) stream))
  (define Y '())
  (if (not (good xs))
      (set! error #t)
      (let loop ((slashed? #f) (token (next stream)))
        (if token
            (if (slash? token)
                (if (= (length X) 0)
                    (set! error #t)
                    (loop #t (next stream)))
                (if (sign? token)
                    (set! error #t)
                    (if (char-numeric? token)
                        (begin
                          (if slashed? (set! Y (append Y (list token))) (set! X (append X (list token))))
                          (loop slashed? (next stream))
                          )
                        (set! error #t)
                        )
                    )
                )
            )
        )
      )
  (if (= (length Y) 0)
      #f
      (not error))
  )


(define (list->number xs)
  (if (equal? (car xs) '-)
      (let loop1 ((i (- (length xs) 1)) (num 0))
        (let ((x (- (char->integer (list-ref xs i)) 48)))
          (if (= i 1)
              (- (+ num (* (expt 10 (- (length xs) i 1)) x)))
              (loop1 (- i 1) (+ num (* (expt 10 (- (length xs) i 1)) x)))
              )
          )
        )
      (let loop2 ((i (- (length xs) 1)) (num 0))
        (let ((x (- (char->integer (list-ref xs i)) 48)))         
          (if (= i 0)
              (+ num (* (expt 10 (- (length xs) i 1)) x))
              (loop2 (- i 1) (+ num (* (expt 10 (- (length xs) i 1)) x)))
              )
          )
        )
      )
  )
(define (good xs)
  (and (not (equal? "" xs)))
  )

(define (scan-frac xs)
  
  (define stream (make-stream xs))
  (display "") ;; А почему если это убрать, то ничего не работает?
  (define error #f)
  (define X (minus_or_nothing (peek stream) stream))
  (define Y '())
  (if (not (good xs))
      (set! error #t)
      (let loop ((slashed? #f) (token (next stream)))
        (if token
            (if (slash? token)
                (if (= (length X) 0)
                    (set! error #t)
                    (loop #t (next stream)))
                (if (sign? token)
                    (set! error #t)
                    (if (char-numeric? token)
                        (begin
                          (if slashed? (set! Y (append Y (list token))) (set! X (append X (list token))))
                          (loop slashed? (next stream))
                          )
                        (set! error #t)
                        )
                    )
                )
            )
        )
      )
  (if (= (length Y) 0)
      #f
      (and (not error) (/ (list->number X) (list->number Y))))
  )



(define (scan-many-fracs xs)
  
  (define shit '(#\space #\tab #\newline))
  (define stream (make-stream xs))
  (display "") ;; А почему если это убрать, то ничего не работает?
  
  (define error #f)
  (define out '())
  (define X '())
  (define Y '())
  (if (not (good xs))
      (set! error #t)
      (let loop ((slashed? #f) (token (next stream)) (in_frac #f))
        (if token
            (if (member token shit)
                (if in_frac
                    (if (= (length Y) 0)
                        (set! error #t)
                        (begin (set! out (append out (list (/ (list->number X) (list->number Y))))) (set! X '()) (set! Y '()) (loop #f (next stream) #f)))
                    (begin (set! X '()) (set! Y '()) (loop #f (next stream) #f)))
                (if (slash? token)
                    (if slashed?
                        (set! error #t)
                        (if (= (length X) 0)
                            (set! error #t)
                            (loop #t (next stream) #t)))
                    (if (sign? token)
                        (if (equal? X '())
                            (if (equal? token #\-)
                                (begin (set! X '(-)) (loop #f (next stream) #t))
                                (loop #f (next stream) #t))
                            (if in_frac
                                (set! error #t)
                                (begin (set! X '()) (loop #f (next stream) #f))))
                        (if (char-numeric? token)
                            (begin
                              (if slashed?
                                  (set! Y (append Y (list token)))
                                  (set! X (append X (list token))))
                              (loop slashed? (next stream) #t))           
                                (set! error #t)
                            )
                        )
                        
                    )
                )
            (or (= (length Y) 0) 
                (begin (set! out (append out (list (/ (list->number X) (list->number Y))))) (set! X '()) (set! Y '()))))))
  (if (= (length out) 0)
                (set! error #t))
  (and (not error) out)
  )

(display "check-frac:\n")
(check-frac "110/111") ;; ⇒ #t
(check-frac "-4/3")    ;; ⇒ #t
(check-frac "+5/10")   ;; ⇒ #t
(check-frac "5.0/10")  ;; ⇒ #f
(check-frac "FF/10")   ;; ⇒ #f
(check-frac "/0")

(display "\nscan-frac:\n")
(scan-frac "110/111")  ;; ⇒ 110/111
(scan-frac "-4/3")     ;; ⇒ -4/3
(scan-frac "+5/10")    ;; ⇒ 1/2 
(scan-frac "5.0/10")   ;; ⇒ #f
(scan-frac "FF/10")    ;; ⇒ #f
(scan-frac "1/") 

(display "\nscan-many-fracs:\n")
(scan-many-fracs
 "\t1/2 1/3\n\n10/8")  ;; ⇒ (1/2 1/3 5/4)
(scan-many-fracs
 "\t1/2 1/3\n\n2/-5")  ;; ⇒ #f

(scan-many-fracs "")
(scan-many-fracs "/2")
(scan-many-fracs "1/")
(scan-many-fracs "/1")
(scan-many-fracs "1/1 ")

(display "-----\n")

