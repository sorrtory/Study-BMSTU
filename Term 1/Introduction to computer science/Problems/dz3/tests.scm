(define (mysimplify xs)  ;; Фукция mysimplify
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

(define-syntax myflatten  ;; Макрос mymyflatten
  (syntax-rules ()
    ((myflatten xxs)
     (let loop ((xs xxs))      
       (if (list? xs)
           (if (= (length xs) 1)
               (loop (car xs))
               (append (loop (car xs)) (loop (cdr xs)))
               )
           (list xs)
           )))))


(define (x_inside? xs)
  (and (member 'x (myflatten xs))
      #t
      )
  )
(define (der*2 xs last)
  (display "der*2) xs:  ")
  (display xs)
  (display "  last: ")
  (display last)
  (newline)
  (if (null? (cdddr xs))
      (if (null? (cddr xs))
          (cadr xs)
          `(+ (* ,(cadr xs) ,(caddr xs)) (* ,last ,(derivative (caddr xs)))))
      (der*2 `(* ,(der* `(* ,(cadr xs) ,(caddr xs))) ,@(cdddr xs)) `(* ,(cadr xs) ,(caddr xs)))
      )
      
  )
  


(define (der* xs)  
  (if (null? (cddr xs))
      (cadr xs)
      (if (null? (cdddr xs))
          (cond
            ((and (x_inside? (cadr xs)) (x_inside? (caddr xs))) (mysimplify `(+ ,(mysimplify `(* ,(derivative (cadr xs)) ,(caddr xs))) ,(mysimplify `(* ,(cadr xs) ,(derivative (caddr xs)))))))
            ((and (x_inside? (cadr xs)) (not (x_inside? (caddr xs)))) (mysimplify `(* ,(derivative (cadr xs)) ,(caddr xs))))
            ((and (not (x_inside? (cadr xs))) (x_inside? (caddr xs))) (mysimplify `(* ,(cadr xs) ,(derivative (caddr xs))))))
          (der*2 xs 1)
      )
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
     (der* xs)
     )
     
    ((equal? (car xs) '/)  ;; Деление
     `(/ ,(mysimplify `(- ,(mysimplify `(* ,(derivative (cdr xs)) ,(caddr xs))) ,(mysimplify `(* ,(cadr xs) ,(derivative (caddr xs)))))) (expt ,(caddr xs) 2)))

    ((equal? (car xs) 'expt)  ;; Степень
     (if (x_inside? (cadr xs))
         (mysimplify `(* ,(caddr xs) (expt ,(cadr xs) ,(- (caddr xs) 1)))) ;; Степенная
         (mysimplify `(* ,xs (log ,(cadr xs)))) ;; Показательная
         ))
        
    ((equal? (car xs) '-)
     (if (null? (cddr xs))
          `(- ,(derivative (cadr xs)))
          (mysimplify `(- ,(derivative (cadr xs)) ,(derivative (caddr xs)))))) ;; Минус
    
    ((equal? (car xs) '+) (mysimplify `(+ ,(derivative (cadr xs)) ,(derivative (caddr xs))))) ;; Плюс
    
    ((equal? (car xs) 'cos) (mysimplify `(* ,(mysimplify `(* -1 ,(derivative (cadr xs)))) (sin ,(cadr xs))))) ;; Косинус
    ((equal? (car xs) 'sin) (mysimplify `(* ,(derivative (cadr xs)) (cos ,(cadr xs))))) ;; Cинус
    
    ((equal? (car xs) 'exp) (mysimplify `(* ,(derivative (cadr xs)) (exp ,(cadr xs)))))  ;; Экспонента

    ((equal? (car xs) 'log) (mysimplify `(* ,(derivative (cadr xs)) (/ 1 ,(cadr xs)))))  ;; Лонорифм
    )
  )


;; Тесты
;; (mysimplify (derivative '(expt x 3)))
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

(define ie (interaction-environment))

(define-syntax derivative-test
  (syntax-rules ()
    ((derivative-test argument expected call-arg)
     (test (round_1e-6 (eval `(let ((x call-arg))
                                ,(derivative 'argument))
                             ie))
           (round_1e-6 (eval '(let ((x call-arg))
                                expected)
                             ie))))))

(define PI (* 4 (atan 1)))

(define (round_1e-6 x)
  (/ (round (* x 1e6)) 1e6))


(display "\n-=РОБОТ-ПРОВЕРЯЛЬЩИК ВЫПОЛНЯЕТ ТЕСТЫ ДЛЯ ПРОИЗВОДНОЙ=-\n\n")

(display (derivative '(* 2 (sin x) (cos x))))
(newline)
;;(display (derivative '(* 2 (sin x))))
(define tests
  (list
   
   (derivative-test 2 0 10.5252)
   (derivative-test x 1 10.5252)
        (derivative-test (- x) -1 10.5252)
        (derivative-test (* 1 x) 1 10.5252)
        (derivative-test (* -1 x) -1 10.5252)
        
        (derivative-test (* -4 x) -4 10.5252)
        (derivative-test (* x 10) 10 10.5252)
        (derivative-test (- (* 2 x) 3) 2 10.5252)
        (derivative-test (expt x 10) (* 10 (expt x 9)) 10.5252)
        (derivative-test (* 2 (expt x 5)) (* 10 (expt x 4)) 10.5252)
        (derivative-test (expt x -2) (* -2 (expt x -3)) 10.5252)
        (derivative-test (expt 5 x) (* (log 5) (expt 5 x)) 10.5252)
        (derivative-test (cos x) (- (sin x)) (/ PI 2))
        (derivative-test (sin x) (cos x) 0)
        (derivative-test (sin x) (cos x) 0.5252)
        (derivative-test (exp x) (exp x) 10.5252)
        (derivative-test (* 2 (exp x)) (* 2 (exp x)) 10.5252)
        (derivative-test (* 2 (exp (* 2 x))) (* 4 (exp (* 2 x))) 10.5252)
        (derivative-test (log x) (/ 1 x) 7.5252)
        (derivative-test (* (log x) 3) (/ 3 x) 7.5252)
        (derivative-test (+ (expt x 3) (* x x)) (+ (* 3 x x) (* 2 x)) 10.5252)
        (derivative-test (- (* 2 (expt x 3)) (* 2 (expt x 2)))
                         (- (* 6 x x) (* 4 x))
                         10.5252)
        (derivative-test (/ 3 x) (/ -3 (* x x)) 7.5252)
        (derivative-test (/ 3 (* 2 (expt x 2))) (/ -3 (expt x 3)) 7.5252)
        (derivative-test (* 2 (sin x) (cos x))
                         (* 2 (cos (* 2 x)))
                         (/ PI 3))
        (derivative-test (* 2 (exp x) (sin x) (cos x))
                         (* (exp x) (+ (* 2 (cos (* 2 x))) (sin (* 2 x))))
                         0.5252) 
        (derivative-test (cos (* 2 (expt x 2)))
                         (* -4 x (sin (* 2 (expt x 2))))
                         5.5252)
        (derivative-test (sin (log (expt x 2)))
                         (/ (* 2 (cos (log (expt x 2)))) x)
                         15.5252)
        (derivative-test (+ (sin (+ x x)) (cos (* x 2 x)))
                         (+ (* 2 (cos (* 2 x))) (* -4 (sin (* x 2 x)) x))
                         10.5252)
        (derivative-test (* (sin (+ x x)) (cos (* x 2 x)))
                         (+ (* (- 1 (* 2 x)) (cos (* 2 x (- 1 x))))
                            (* (+ 1 (* 2 x)) (cos (* 2 x (+ 1 x)))))
                         5.5252)
        )
  )


(define **test-succeed-5252** (run-tests tests))