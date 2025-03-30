(define (make-multi-vector size . fill)
  (if (null? fill) (set! fill 0))
  (list->vector (append '("mvec") (list size) (vector->list (make-vector (apply * size) fill))))
  )

(define (multi-vector? m) (and (vector? m) (equal? (vector-ref m 0) "mvec")))

(define (multi-vector-ref vec ind)  
  (let*
      ((lvec (vector->list vec))
       (size (cadr lvec)) ;; Длины
       (ind_len (length size))  ;; Кол-во длин
       )
    (let loop ((vec_i 2) (i 0) (ind ind) (size size))
      (if (= i ind_len)
          (vector-ref vec vec_i)
          (loop (+ vec_i (* (apply * (cdr size)) (car ind))) (+ i 1) (cdr ind) (cdr size))
          )
      )
    )
  )

(define (multi-vector-set! vec ind xs)  
  (let*
      ((lvec (vector->list vec))
       (size (cadr lvec)) ;; Длины
       (ind_len (length size))  ;; Кол-во длин
       )
    (let loop ((vec_i 2) (i 0) (ind ind) (size size))
      (if (= i ind_len)
          (vector-set! vec vec_i xs)
          (loop (+ vec_i (* (apply * (cdr size)) (car ind))) (+ i 1) (cdr ind) (cdr size))
          )
      )
    )
  )




(define m (make-multi-vector '(11 12 9 16)))
(multi-vector? m)
(multi-vector-set! m '(10 7 6 12) 'test)
(multi-vector-ref m '(10 7 6 12)) ;; ⇒ test

; Индексы '(1 2 1 1) и '(2 1 1 1) — разные индексы
(multi-vector-set! m '(1 2 1 1) 'X)
(multi-vector-set! m '(2 1 1 1) 'Y)
(multi-vector-ref m '(1 2 1 1)) ;; ⇒ X
(multi-vector-ref m '(2 1 1 1)) ;; ⇒ Y

(define m (make-multi-vector '(3 5 7) -1))
(multi-vector-ref m '(0 0 0)) ;; ⇒ -1
