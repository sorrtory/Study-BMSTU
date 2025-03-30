(define (roots a b c)
  (define d (- (* b b) (* 4 a c)))
  
  (cond
    ((> d 0) (list (/ (+ (- 0 b) (sqrt d)) (* 2 a)) (/ (+ (+ 0 b) (sqrt d)) (* 2 a))))
    ((= d 0) (list (/ (+ (- 0 b) (sqrt d)) (* 2 a))))
    ((< d 0) (list ))
    )
  )

(roots 1 2 -3)
(roots 1 -2 -5)
(roots 1 -2 1)
(roots 1 -2 100)
