(define (trib n)
  (cond ((<= n 1) 0)
        ((= n 2) 1)
        ((> n 2) (+ (trib (- n 1)) (trib (- n 2)) (trib (- n 3)))
        )
  )
)

(define trib-memo
  (let ((known-results '()))
    (lambda (n)
      (let ((res (assoc n known-results)))
        (if res
            (cadr res)
            (let
                ((res (cond ((<= n 1) 0)
                              ((= n 2) 1)
                              ((> n 2) (+ (trib-memo (- n 1)) (trib-memo (- n 2)) (trib-memo (- n 3)))))))
              (set! known-results (cons (list n res) known-results))
              res))))))


(trib 30)
(trib-memo 50)
(trib 50)
