
(define-syntax trace-ex
  (syntax-rules ()
    ((trace-ex xss)
     (let ((x xss))
       (write (quote x))
       (display " => ")
       (write x)
       (newline)
       x
       )
     )
    )
  )

