(define (count a l)
  (if (= (length l) 0)
      0
      (if (equal? a (car l))
          (+ 1 (count a (cdr l)))
          (count a (cdr l))
          )))

(count 'a '(a b c a))
(count 'b '(a c d))
(count 'a '())
      
