(define shit '(#\space #\tab #\newline))
(define (string-trim-left xs)
  (define l (string-length xs))
  (let loop ((i 0))
    (if (member (string-ref xs i) shit) 
        (loop (+ i 1))
        (substring xs i l)
        )
    )
  )
 
(define (string-trim-right xs)
  (define l (string-length xs))
  (let loop ((i 1))
    (if (member (string-ref xs (- l i)) shit) 
        (loop (+ i 1))
        (substring xs 0 (+ 1 (- l i)))
        )
    )
  )

(define (string-trim xs)
  (string-trim-right (string-trim-left xs))
  )

(define (string-prefix? a  b)
  (define la (string-length a))
  (define lb (string-length b))
  (and (<= la lb) (equal? a (substring b 0 la)))
  )

(define (string-suffix? a  b)
  (define la (string-length a))
  (define lb (string-length b))
  
  (and (<= la lb) (equal? a (substring b (- lb la) lb)))
  )

(define (string-infix? a  b)
  (define la (string-length a))
  (define lb (string-length b))
  
  (let loop ((out (<= la lb) )(i 0))
    (if (or (> i (- lb la)) (and out (> i 0)))
        out
        (loop (string-prefix? a (substring b i lb)) (+ i 1))
        )
    )
  )

(define (string-split xs symb)
  (define lxs (string-length xs))
  (define lsymb (string-length symb))

  
  (define (skip? xs symb i)
    (define lxs (string-length xs))
    (define lsymb (string-length symb))
    
    (and (< (+ i lsymb) lxs)
        (equal? (substring xs i (+ i lsymb)) symb
        )
      )
    )

  (let loop ((out '()) (i 0))
    (if (= i lxs)
        (map (lambda (x) (make-string 1 x)) out)
        (if (skip? xs symb i)
            (loop out (+ i lsymb))
            (loop (append out `(,(string-ref xs i))) (+ i 1))
            )
        )
    )
  
  )


(display "Trim\n")
(string-trim-left  "\t\tabc def")   ;; ⇒ "abc def"
(string-trim-right "abc def\t")     ;; ⇒ "abc def"
(string-trim       "\t abc def \n") ;; ⇒ "abc def"

(display "Fix\n")
(string-prefix? "abc" "abcdef")  ;; ⇒ #t
(string-prefix? "bcd" "abcdef")  ;; ⇒ #f
(string-prefix? "abcdef" "abc")  ;; ⇒ #f

(display "---\n")
(string-suffix? "def" "abcdef") ;;  ⇒ #t
(string-suffix? "bcd" "abcdef")  ;; ⇒ #f

(display "---\n")
(string-infix? "def" "abcdefgh") ;; ⇒ #t
(string-infix? "abc" "abcdefgh") ;; ⇒ #t
(string-infix? "fgh" "abcdefgh") ;; ⇒ #t
(string-infix? "ijk" "abcdefgh") ;; ⇒ #f
(string-infix? "bcd" "abc")      ;; ⇒ #f

(display "Split\n")

(string-split "x;y;z" ";")       ;; ⇒ ("x" "y" "z")
(string-split "x-->y-->z" "-->") ;; ⇒ ("x" "y" "z")
