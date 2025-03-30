(define (any? pred xs)
  (and (not(null? xs)) (or (pred (car xs)) (any? pred (cdr xs))) )
  )

(define (all? pred xs)
  (or (null? xs) (and (pred (car xs)) (any? pred (cdr xs))) )
  )


(any? odd? '(1 3 5 7)) ;; ⇒ #t
(any? odd? '(0 1 2 3)) ;; ⇒ #t
(any? odd? '(0 2 4 6)) ;; ⇒ #f
(any? odd? '()) ;; ⇒ #f
(display "---\n")
(all? odd? '(1 3 5 7)) ;; ⇒ #t
(all? odd? '(0 1 2 3)) ;; ⇒ #f
(all? odd? '(0 2 4 6)) ;; ⇒ #f
(all? odd? '()) ;; ⇒ #t ;; Это - особенность, реализуйте её