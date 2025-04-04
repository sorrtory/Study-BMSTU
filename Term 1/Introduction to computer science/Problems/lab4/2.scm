(define (save-data data path)
  (call-with-output-file path
    (lambda (port)
      (display data port))))

(define (load-data path)
  (define (read-chars path)
    (call-with-input-file path
      (lambda (port)
        (let loop ((x (read-char port)))
          (cond 
            ((eof-object? x) '())
            (else (begin (cons x (loop (read-char port))))))))))
  (apply string (read-chars path)))


(define data 'hello123)
(define path "texxxt.txt")

(save-data data path)
(load-data path)

(define (count_lines path)
  (define (read-chars path)
    (call-with-input-file path
      (lambda (port)
        (let loop ((x (read-char port)) (s 0) (c 0))
          (cond 
            ((eof-object? x)
             (if (= c 0)
                 (if (> s 0) 1 0)
                 c))
            (else
             (if (equal? #\newline x)
                 (if (> s 0)
                     (begin (loop (read-char port) 0 (+ c 1)))
                     (begin (loop (read-char port) 0 c)))
                 (begin (loop (read-char port) (+ s 1) c)))))))))
  (read-chars path))

(count_lines "text.txt")
(count_lines path)

