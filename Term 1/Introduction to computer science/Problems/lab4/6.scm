(define-syntax when
  (syntax-rules ()
    ((when cond . exprs) (if cond (begin . exprs)))
    ))

(define-syntax unless
  (syntax-rules ()
    ((unless cond . exprs) (if (not cond) (begin . exprs)))
    ))

(display "--When--\n")
(define x 1)
(when (> x 0) (display "x > 0") (newline)) ;; x > 0
(unless (= x 0) (display "x != 0") (newline)) ;; x != 0

(display "--For--\n")

(define-syntax for
  (syntax-rules (in as)
    ((for i in vars exprs ...)
     (let loop ((var vars))
       (if (not (null? var))
           (let ((i (car var)))
             exprs ...
             (loop (cdr var)))
           )
       )
     )
    ((for vars as i exprs ...)
     (let loop ((var vars))
       (if (not (null? var))
           (let ((i (car var)))
             exprs ...
             (loop (cdr var)))
           )
       )
     )
    )
  )

(for i in '(1 2 3)
  (for j in '(4 5 6)
    (display (list i j))
    (newline)))

(newline)

(for '(1 2 3) as i
  (for '(4 5 6) as j
    (display (list i j))
    (newline)))

(display "--While--\n")

(define-syntax while
  (syntax-rules ()
    ((while cond body ...)
      (let loop ()
        (when cond
          body ...
          (loop)
        )
      )
    )
  )
)


(let ((p 0)
      (q 0))
  (while (< p 3)
         (set! q 0)
         (while (< q 3)
                (display (list p q))
                (newline)
                (set! q (+ q 1)))
         (set! p (+ p 1))))


(display "--Repeat..until--\n")

(define-syntax repeat
  (syntax-rules (until)
    ((repeat (body ...) until cond)
      (let loop ()
        body ...
        (unless cond
          (loop)
        )
      )
    )
  )
)

(repeat
 ((display 'hello))
 until (= (* 2 2) 4))


(let ((i 0)
      (j 0))
  (repeat ((set! j 0)
           (repeat ((display (list i j))
                    (set! j (+ j 1)))
                   until (= j 3))
           (set! i (+ i 1))
           (newline))
          until (= i 3)))

(display "--C++--\n")

(define-syntax cout
  (syntax-rules (<< endl)
    ((cout << endl)
      (newline)
    )
    ((cout << endl exprs ...)
      (begin (newline) (cout exprs ...))
    )
    ((cout << expr)
      (display expr)
    )
   ((cout << expr exprs ...)
      (begin (display expr) (cout exprs ...))
    )

  )
)

(cout << "a = " << 1 << endl << "b = " << 2 << endl)