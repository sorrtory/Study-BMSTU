(load "trace.scm")

(display "Example 1\n")
;#;
(define (zip . xss)
  (if (or (null? xss)
          (null? (trace-ex (car xss)))) ; Здесь...
      '()
      (cons (map car xss)
            (apply zip (map cdr (trace-ex xss)))))) ; ... и здесь


(zip '(1 2 3) '(one two three))

;; 
(display "\nExample 2\n")


(define counter
  (let ((n 0))
    (lambda () (set! n (+ n 1)) n)))

(+ (trace-ex (counter)) (trace-ex (counter)))

