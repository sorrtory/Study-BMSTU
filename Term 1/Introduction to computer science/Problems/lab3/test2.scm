; Пример процедуры с ошибкой
; 
(define (signum x)
  (cond
    ((< x 0) -1)
    ((= x 0)  1) ; Ошибка здесь!
    (else     1)))

; Загружаем каркас
;
(load "unit-test.scm")

; Определяем список тестов
;
(define the-tests
  (list (test (signum -2) -1)
        (test (signum  0)  0)
        (test (signum  2)  1)))

(display "Example 1\n")
; Выполняем тесты
;
(run-tests the-tests)

(display "\nExample 2\n")

(define counter
  (let ((n 0))
    (lambda () (set! n (+ n 1)) n)))

;; Дано 2 вызова 
(counter) 
(counter) 

(define counter-tests
  (list
   (test (counter) 3)
   (test (counter) 8)
   (test (counter) 5))
  )
(run-tests counter-tests)