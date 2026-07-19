' Суммирование элементов массива
Function SumArray#(Values#(nValues%))
SumArray#=0
For i%=1 To nValues%
SumArray#=SumArray#+Values#(i%)
Next i%
End Function

' Вычисление многочлена по схеме Горнера
Function Polynom!(x!,coefs!(ncoefs%))
Polynom!=0
For i%=1 to ncoefs%
Polynom!=Polynom!*x!+_
coefs!(i%)
Next i%
End Function

Function Polynom1111!(x!)
Dim coefs!(4)

For i%=1 To 4
coefs!(i%)=1
Next i%

Polynom1111!=Polynom!(x!,coefs!)
End Function

Sub Fibonacci(res&(n%))
If n%>=1 Then
res&(1)=1
End If
If n%>=2 Then
res&(2)=1
End If
i%=3
Do While i%<=n%
res&(i%)=res&(i%-1)+res&(i%-2)
i%=i%+1
Loop
End Sub

Function Join$(sep$,items$(count%))
If count%>=1 Then
Join$=items$(1)
Else
Join$=""
End If
For i%=2 To count%
Join$=Join$+sep$+items$(i%)
Next i%
End Function
