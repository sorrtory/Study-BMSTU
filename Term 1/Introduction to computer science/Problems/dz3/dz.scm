;;;;;;;;;;;;;;;;;;;;; IN TESTS.SCM

(define (simplify xs)  ;; Фукция simplify
  (if (equal? (car xs) '*)
      (if (or (equal? '0 (cadr xs)) (equal? '0 (caddr xs)))
          '0
          (if (or (equal? '1 (cadr xs)) (equal? '1 (caddr xs)))
              (if (equal? '1 (cadr xs))
                  (caddr xs)
                  (cadr xs)
                  )
              xs
              )    
          )
      (if (equal? (car xs) '+)
          (if (or (equal? '0 (cadr xs)) (equal? '0 (caddr xs)))
              (if (equal? '0 (cadr xs))
                  (caddr xs)
                  (cadr xs)
                  )
              xs
              )
          (if (equal? (car xs) '-)
              (if (equal? '0 (caddr xs))
                  (cadr xs)
                  (if (equal? '0 (cadr xs))
                      `(- ,(caddr xs))
                      xs)
                  )
              xs
              )
          )
      )
  )

(define-syntax flatten  ;; Макрос flatten
  (syntax-rules ()
    ((flatten xxs)
     (let loop ((xs xxs))      
       (if (list? xs)
           (if (= (length xs) 1)
               (loop (car xs))
               (append (loop (car xs)) (loop (cdr xs)))
               )
           (list xs)
           )))))


(define (x_inside? xs)
  (and (member 'x (flatten xs))
      #t
      )
  )

(define (derivative xs)
  ;; (display "\n")
  ;; (display xs)
  (cond
    ((integer? xs) 0)
    ((equal? xs 'x) '1)
    ((integer? (car xs)) 0) ;; Константа
    ((equal? (car xs) 'x) 1)
    ((equal? (car xs) '-x) -1)
    
    ((equal? (car xs) '*) ;; Умножение
     (cond
       ((and (x_inside? (cadr xs)) (x_inside? (caddr xs))) (simplify `(+ ,(simplify `(* ,(derivative (cadr xs)) ,(caddr xs))) ,(simplify `(* ,(cadr xs) ,(derivative (caddr xs)))))))
       ((and (x_inside? (cadr xs)) (not (x_inside? (caddr xs)))) (simplify `(* ,(derivative (cadr xs)) ,(caddr xs))))
       ((and (not (x_inside? (cadr xs))) (x_inside? (caddr xs))) (simplify `(* ,(cadr xs) ,(derivative (caddr xs)))))
         )
     )
     
    ((equal? (car xs) '/)  ;; Деление
     `(/ ,(simplify `(- ,(simplify `(* ,(derivative (cdr xs)) ,(caddr xs))) ,(simplify `(* ,(cadr xs) ,(derivative (caddr xs)))))) (expt ,(caddr xs) 2)))

    ((equal? (car xs) 'expt)  ;; Степень
     (if (x_inside? (cadr xs))
         (simplify `(* ,(caddr xs) (expt ,(cadr xs) ,(- (caddr xs) 1)))) ;; Степенная
         (simplify `(* ,xs (log ,(cadr xs)))) ;; Показательная
         ))
        
    ((equal? (car xs) '-) (simplify `(- ,(derivative (cadr xs)) ,(derivative (caddr xs))))) ;; Минус
    ((equal? (car xs) '+) (simplify `(+ ,(derivative (cadr xs)) ,(derivative (caddr xs))))) ;; Плюс
    
    ((equal? (car xs) 'cos) (simplify `(* ,(simplify `(* -1 ,(derivative (cadr xs)))) (sin ,(cadr xs))))) ;; Косинус
    ((equal? (car xs) 'sin) (simplify `(* ,(derivative (cadr xs)) (cos ,(cadr xs))))) ;; Cинус
    
    ((equal? (car xs) 'exp) (simplify `(* ,(derivative (cadr xs)) (exp ,(cadr xs)))))  ;; Экспонента

    ((equal? (car xs) 'log) (simplify `(* ,(derivative (cadr xs)) (/ 1 ,(cadr xs)))))  ;; Лонорифм

    
    )
    
  )


;; Тесты
;; (simplify (derivative '(expt x 3)))
;; (derivative '(expt x 5)) ;; ⇒ (* 10 (expt x 9))
;; (derivative '(* 2 (expt x 5))) ;; ⇒ (* 2 (* 5 (expt x 4)))
;; (derivative (list '* 'x 'x)) ;; ⇒ (+ (* x 1) (* 1 x))






(define-syntax test
  (syntax-rules ()
    ((test returned expected) (list (quote returned) returned expected))))

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
           #f)))))

(define-syntax run-tests
  (syntax-rules ()
    ((run-tests test_obj_list)
     (not (member #f (map (lambda (n) (run-test n)) test_obj_list))))))

#|
(define the-tests
  ;; Если выпала ошибка, можно попробовать подставить произвольное число x в предложенную и в полученную производную.
  ;; Если результаты совпадут, то ошибка была вызвана различной формой записи производных, а предложенный ответ является верным
  
  (list
   
   (test (derivative '(2)) 0)
   (test (derivative  '(x))  1)
   (test (derivative  '(-x))  -1)
   (test (derivative  '(* 1 x))  1)
   (test (derivative  '(* -1 x))  -1)
   (test (derivative  '(* -4 x))  -4)
   (test (derivative  '(* 10 x))  10)
   (test (derivative  '(- (* 2 x) 3))  2)
   (test (derivative  '(expt x 10))  '(* 10 (expt x 9)))
   (test (derivative  '(* 2 (expt x 5)))  '(* 2 (* 5 (expt x 4))))
   (test (derivative  '(expt x -2))  '(* -2 (expt x -3)))

   (test (derivative  '(expt 5 x))  '(* (expt 5 x) (log 5)))
   (test (derivative  '(cos x))  '(* -1 (sin x)))
   (test (derivative  '(sin x))  '(cos x))
   (test (derivative  '(exp x))  '(exp x))
   (test (derivative  '(* 2 (exp x)))  '(* 2 (exp x)))
   (test (derivative  '(* 2 (exp (* 2 x))))  '(* 2 (* 2 (exp (* 2 x)))))
   (test (derivative  '(log x))  '(/ 1 x))
   (test (derivative  '(* 3 (log x)))  '(* 3 (/ 1 x)))
   (test (derivative  '(+ (expt x 3) (expt x 2)))  '(+ (* 3 (expt x 2)) (* 2 (expt x 1))))
   (test (derivative  '(- (* 2 (expt x 3)) (* 2 (expt x 2))))  '(- (* 2 (* 3 (expt x 2))) (* 2 (* 2 (expt x 1)))))
   
   (test (derivative  '(/ 3 x))  '(/ (- 3) (expt x 2)))
   (test (derivative  '(/ 3 (* 2 (expt x 2))))  '(/ (- (* 3 (* 2 (* 2 (expt x 1))))) (expt (* 2 (expt x 2)) 2)))
   (test (derivative  '(* 2 (* (sin x) (cos x))))  '(* 2 (+ (* (cos x) (cos x)) (* (sin x) (* -1 (sin x))))))
   (test (derivative  '(* 2 (* (* (exp x) (sin x)) (cos x))))  '(* 2 (+ (* (+ (* (exp x) (sin x)) (* (exp x) (cos x))) (cos x)) (* (* (exp x) (sin x)) (* -1 (sin x))))))  ;; (+ (* (exp 1) (sin 2)) (* 2 (exp 1) (cos 2))) ;; checked
   
   (test (derivative  '(sin (* 2 x)))  '(* 2 (cos (* 2 x))))
   (test (derivative  '(cos (* 2 (expt x 2))))  '(* (* -1 (* 2 (* 2 (expt x 1)))) (sin (* 2 (expt x 2)))))  ;; (* 4 (- (sin (* 2 (expt x 2)))))
   (test (derivative  '(sin (log (expt 2))))  '(* (* (* (expt 2) (log 2)) (/ 1 (expt 2))) (cos (log (expt 2)))))
   (test (derivative  '(+ (sin (* 2 x)) (cos (* 2 (expt x 2)))))   '(+ (* 2 (cos (* 2 x))) (* (* -1 (* 2 (* 2 (expt x 1)))) (sin (* 2 (expt x 2))))))
   (test (derivative  '(* (sin (* 2 x)) (cos (* 2 (expt x 2)))))   '(+ (* (* 2 (cos (* 2 x))) (cos (* 2 (expt x 2)))) (* (sin (* 2 x)) (* (* -1 (* 2 (* 2 (expt x 1)))) (sin (* 2 (expt x 2)))))))
   
      )
  )

(display "Test\n")
; Выполняем тесты
(run-tests the-tests)

|#