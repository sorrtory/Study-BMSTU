(define (my-gcd aa bb)
  (define a (abs aa))
  (define b (abs bb))
  
  (cond
    ((= a b) a)
    ((> a b)
     (if (zero? (remainder a b))
         b
         (my-gcd b (remainder a b)))
     )
    ((< a b)
     (if (zero? (remainder b a))
         a
         (my-gcd a (remainder b a)))
     )
    )
  )
(define (_prime a b)
  (or (= a b)
      
      (and (= (my-gcd a b) 1)
          (_prime a (+ b 1))
          
          )
      )
  )

  
(define (prime? a)
  (_prime a 2)
  )

(define (my-lcm a b)
  (/ (* a b) (my-gcd a b))
  )


