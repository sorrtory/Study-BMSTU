
(define (iterate f x n)
  (if (<= n 0)
      '()
      (cons x (iterate f (f x) (- n 1))) ))








(iterate (lambda (x) (* 2 x)) 1 6)
(iterate (lambda (x) (* 2 x)) 1 1)
(iterate (lambda (x) (* 2 x)) 1 0)