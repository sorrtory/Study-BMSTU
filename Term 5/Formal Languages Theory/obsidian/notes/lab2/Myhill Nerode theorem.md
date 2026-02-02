
[wiki](https://en.wikipedia.org/wiki/Myhill%E2%80%93Nerode_theorem)

Key idea:  
Two words x,yx, yx,y are **Myhill–Nerode equivalent** for language LLL if for **every** suffix zzz


$$

\begin{align*}

xz∈L  ⟺  yz∈L \\
xz \in L \iff yz \in L \\
xz∈L⟺yz∈L. 

\end{align*}
$$

Intuitively: no suffix can distinguish xxx from yyy with respect to membership in LLL.


Если в табличке плюсюки совпадают, тогда это один класс эквивалентности

поэтому набираем суффиксов до тех пор пока у нас не получится что каждый префикс имеет уникальную комбинацию плюсиков


## 5. How the table uses Myhill–Nerode in practice

You don’t check **all** suffixes (that’d be impossible). You just need, for every pair of prefixes, **some** suffix that distinguishes them. The table is a compact way to organize that.


[video guide](https://youtu.be/Dx2RJ2DXRYs?si=AMg28zkHgN2Oc56s)

