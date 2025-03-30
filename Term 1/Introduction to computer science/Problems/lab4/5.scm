(define-syntax my-let
  (syntax-rules ()
    ((my-let ((var val) ...) body ...)
      ((lambda (var ...) body ...) val ...))))

(my-let ((x 1) (y 4)) (+ x y))

(define-syntax my-let*
  (syntax-rules ()
    ((my-let* () body ...)
      ((lambda () body ...)))
    ((my-let* ((var val) rest ...) body ...)
      ((lambda (var) (my-let* (rest ...) body ...)) val))))

(my-let* ((x 5) (y (+ 10 x))) (+ x y))
