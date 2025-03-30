(define-syntax test
  (syntax-rules ()
    ((test returned expected) (list (quote returned) returned expected))
    )
  )

(define-syntax run-test
  (syntax-rules ()
    ((run-test test_obj)
     (if (equal? (cadr test_obj) (caddr test_obj))
         (begin (write (car test_obj)) (display " ok\n") #t)
         (begin
           (write (car test_obj))
           (display " FAIL\n")
           (display "  Expected: ")
           (write (caddr test_obj))
           (newline)
           (display "  Returned: ")
           (write (cadr test_obj))
           (newline)
           #f)
         )
     )
    )
  )

(define-syntax run-tests
  (syntax-rules ()
    ((run-tests test_obj_list)
     (not (member #f (map (lambda (n) (run-test n)) test_obj_list)))
     )
    )
  )
  