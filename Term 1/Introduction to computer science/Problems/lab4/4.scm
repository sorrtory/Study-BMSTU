
(define-syntax my-if
  (syntax-rules ()
    ((my-if expr thn els)
     (let ((tr (delay thn)) (fl (delay els)))
       (force (or (and expr tr) fl))))))

(my-if #t 1 (/ 1 0)) ;; ⇒ 1
(my-if #f (/ 1 0) 1) ;; ⇒ 1