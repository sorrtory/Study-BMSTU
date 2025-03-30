

(define (factorize xs)
  
  (let
      (
       (sign (car xs))
       (x (cadr (cadr xs)))
       (y (cadr (caddr xs)))
       (pwr (caddr (cadr xs)))
       )
    
    (cond
      ((= pwr 2)
       (begin
         (cond
           ((equal? sign '-) `(* (- ,x ,y) (+ ,x ,y)))
           (else #f)
           )
         )
       )
      ((= pwr 3)
       (begin
         (cond
           ((equal? sign '-) `(* (- ,x ,y) (+ (expt ,x 2) (* ,x ,y) (expt ,y 2))))
           ((equal? sign '+) `(* (+ ,x ,y) (+ (- (expt ,x 2) (* ,x ,y)) (expt ,y 2))))
           (else #f)
           )
         )
       )
      (else #f)
      )
    )
  )


;; Tesstss
(load "unit-test.scm")

(define the-tests
  (list (test (factorize '(- (expt x 2) (expt y 2))) '(* (- x y) (+ x y)))
        (test (factorize '(- (expt (+ first 1) 2) (expt (- second 1) 2)))  '(* (- (+ first 1) (- second 1))
                                                                               (+ (+ first 1) (- second 1))))
        (test (factorize  '(- (expt x 3) (expt y 3)))  '(* (- x y) (+ (expt x 2) (* x y) (expt y 2))))))

(run-tests the-tests)
