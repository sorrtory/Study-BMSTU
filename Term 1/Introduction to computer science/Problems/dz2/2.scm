(define (count a l)
  (if (= (length l) 0)
      0
      (if (equal? a (car l))
          (+ 1 (count a (cdr l)))
          (count a (cdr l))
          )))
(define (mem a l)
    (if (= (length l) 0)
        #f
        (if (equal? a (car l))
            #t
            (mem a (cdr l))
            ))
  )

(define (list->set xxs)
  (if (null? xxs)
      '()
      (if (equal? 1 (count (car xxs) xxs))
          (cons (car xxs) (list->set (cdr xxs)))
          (list->set (cdr xxs))
          )
      )
  )

(define (set? xxs)
  (= (length xxs) (length (list->set xxs)))
  )

(define (union s1 s2)
  (list->set (append s1 s2))
  )


(define (intersection s1 s2)
  (let loop ((s '()) (c 0))
    (if (= c (length s1))
        s
        (if (member (list-ref s1 c) s2)
            (loop (append s `(,(list-ref s1 c))) (+ c 1))
            (loop s (+ c 1))
            )
        )
    )
  )
(define (difference s1 s2)
  (define un (union s1 s2))
  (define inter (intersection s1 s2))
  (let loop ((s '()) (c 0))
    (if (= c (length un))
        s
        (if (member (list-ref un c) inter)
            (loop s (+ c 1))
            (loop (append s `(,(list-ref un c))) (+ c 1))
            )
        )
    )
  )
(define (symmetric-difference s1 s2)
  (difference (union s1 s2) (intersection s1 s2))
  )

(define (set-eq? s1 s2)
  (equal? '() (difference s1 s2))
  )
(list->set '(1 1 2 3))                       ;; ⇒ (3 2 1)
(set? '(1 2 3))                              ;; ⇒ #t
(set? '(1 2 3 3))                            ;; ⇒ #f
(set? '())                                   ;; ⇒ #t
(union '(1 2 3) '(2 3 4))                    ;; ⇒ (4 3 2 1)
(intersection '(1 2 3) '(2 3 4))             ;; ⇒ (2 3)
(difference '(1 2 3 4 5) '(2 3))             ;; ⇒ (1 4 5)
(symmetric-difference '(1 2 3 4) '(3 4 5 6)) ;; ⇒ (6 5 2 1)
(set-eq? '(1 2 3) '(3 2 1))                  ;; ⇒ #t
(set-eq? '(1 2) '(1 3))                      ;; ⇒ #f