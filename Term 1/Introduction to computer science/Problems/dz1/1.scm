;;(Year Code + Month Code + Century Code + Date Number - Leap Year Code) mod 7
;; https://artofmemory.com/blog/how-to-calculate-the-day-of-the-week/

(define (year_code y)
  (define YY (remainder y 100))
  (remainder (+ YY (quotient YY 4)) 7)
  )

(define (month_code m)
  (cond
    ((= m 1) 0)
    ((= m 2) 3)
    ((= m 3) 3)
    ((= m 4) 6)
    ((= m 5) 1)
    ((= m 6) 4)
    ((= m 7) 6)
    ((= m 8) 2)
    ((= m 9) 5)
    ((= m 10) 0)
    ((= m 11)3)
    ((= m 12) 5)
    )
  )

(define (centure_code y)
  (define YY (quotient y 100))
  (cond
    ((= YY 17) 4)
    ((= YY 18) 2)
    ((= YY 19) 0)
    ((= YY 20) 6)
    ((= YY 21) 4)
    ((= YY 22) 2)
    ((= YY 23) 0)
    (else (remainder (- 18 YY) 7)
          )
    )
  )

(define (leap_code y m)
  (if (or (= m 0) (= m 1))
      (if (= 0 (remainder y 400))
          -1
          (if (= 0 (remainder y 100))
              0
              (if (= 0 (remainder y 4))
                  -1
                  0
                  )
              )
          )
      0
      )
  )

(define (day-of-week d m y)

  (remainder (+ (year_code y) (month_code m) (centure_code y) (leap_code y m) d) 7)
  )



(day-of-week 04 12 1975) ;; ⇒ 4
(day-of-week 04 12 2006) ;; ⇒ 1
(day-of-week 29 05 2013) ;; ⇒ 3