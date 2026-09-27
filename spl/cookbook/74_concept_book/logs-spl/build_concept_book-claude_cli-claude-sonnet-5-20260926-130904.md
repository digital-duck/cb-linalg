# SPL Run: build_concept_book

- **Adapter:** claude_cli
- **Model:** claude-sonnet-5
- **Tokens:** 1904 in / 1681 out
- **Latency:** 50600ms
- **Timestamp:** 2026-09-26 13:09:04

## Output

```output


---

## Matrix Representation

Every linear transformation $T: \mathbb{R}^n \to \mathbb{R}^m$ can be encoded as a single $m \times n$ matrix $A$, so that computing $T(\mathbf{x})$ reduces to the matrix-vector product $A\mathbf{x}$. The construction relies on a key fact: a linear transformation is completely determined by what it does to a basis. If $\{\mathbf{e}_1, \mathbf{e}_2, \dots, \mathbf{e}_n\}$ is the standard basis of $\mathbb{R}^n$, then any vector $\mathbf{x} = x_1\mathbf{e}_1 + x_2\mathbf{e}_2 + \cdots + x_n\mathbf{e}_n$, and linearity gives

$$T(\mathbf{x}) = x_1 T(\mathbf{e}_1) + x_2 T(\mathbf{e}_2) + \cdots + x_n T(\mathbf{e}_n).$$

This says $T(\mathbf{x})$ is always a linear combination of the vectors $T(\mathbf{e}_1), \dots, T(\mathbf{e}_n)$, with the entries of $\mathbf{x}$ as coefficients. If we place these image vectors as the columns of a matrix,

$$A = \big[\, T(\mathbf{e}_1) \ \ T(\mathbf{e}_2) \ \ \cdots \ \ T(\mathbf{e}_n) \,\big],$$

then $A\mathbf{x}$ computes exactly the sum above — so $T(\mathbf{x}) = A\mathbf{x}$ for every $\mathbf{x}$. The matrix $A$ *is* the transformation, expressed in coordinates.

**Worked example.** Let $T: \mathbb{R}^2 \to \mathbb{R}^2$ rotate every vector counterclockwise by $90^\circ$. Apply $T$ to the standard basis: $T(\mathbf{e}_1) = T(1,0) = (0,1)$, and $T(\mathbf{e}_2) = T(0,1) = (-1,0)$. Stacking these as columns gives

$$A = \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix}.$$

Check it on $\mathbf{x} = (3, 2)$: $A\mathbf{x} = (0\cdot3 + (-1)\cdot2,\ 1\cdot3 + 0\cdot2) = (-2, 3)$, which is indeed $(3,2)$ rotated $90^\circ$ counterclockwise.

**Problem-solving application.** This construction turns geometric or verbal descriptions of a transformation into a computational object you can manipulate — invert, multiply, diagonalize, or feed into software. To find the matrix of *any* linear transformation, you only ever need to do two things: (1) identify what it does to each basis vector, and (2) write those images as columns, in order. This is the standard first move whenever a problem gives you a transformation defined by a rule (rotation, projection, reflection, differentiation on polynomials) and asks you to compute it repeatedly, compose it with another transformation, or analyze its long-term behavior.

---

## Vector Representation

Every vector space $V$ of dimension $n$ over a field $\mathbb{C}$ becomes concrete once we fix an ordered basis $B = (b_1, b_2, \dots, b_n)$. Because $B$ spans $V$ and its vectors are linearly independent, any $w \in V$ can be written as a *unique* linear combination
$$
w = c_1 b_1 + c_2 b_2 + \cdots + c_n b_n.
$$
The coordinate map $\rho_B : V \to \mathbb{C}^n$ sends $w$ to the column vector of these coefficients:
$$
\rho_B(w) = \begin{pmatrix} c_1 \\ c_2 \\ \vdots \\ c_n \end{pmatrix}.
$$
Uniqueness of the coefficients is what makes $\rho_B$ a well-defined function, and it follows directly from linear independence of $B$: if $w$ had two different coordinate representations, subtracting them would produce a nontrivial linear combination of the $b_i$ equal to zero, contradicting independence. Because $\rho_B$ is linear and bijective, it is a **linear isomorphism** — it lets us translate every question about an abstract vector space into a question about ordinary column vectors in $\mathbb{C}^n$, where we already know how to compute.

**Worked example.** Let $V = \mathbb{R}^2$ with the basis $B = (b_1, b_2) = \big((1,1), (1,-1)\big)$. Take $w = (4, 2)$. We solve $c_1(1,1) + c_2(1,-1) = (4,2)$, giving $c_1 + c_2 = 4$ and $c_1 - c_2 = 2$, so $c_1 = 3$, $c_2 = 1$. Thus $\rho_B(w) = (3, 1)^T$. Note that this differs from the standard-basis coordinates $(4,2)$ — the numbers describing $w$ depend entirely on which basis you choose, even though $w$ itself never changes.

**Problem-solving application.** Coordinate maps are the workhorse behind representing linear operators as matrices, changing basis, and computing in coordinate systems adapted to a problem (e.g., eigenbases, which turn a general linear transformation into simple scaling). To find $\rho_B(w)$ for any $w$, solve the linear system $Bc = w$, where $B$ is the matrix whose columns are the basis vectors — equivalently, $c = B^{-1}w$. This single computation — inverting the basis matrix — is the practical core of every basis-change technique you will use later, including diagonalization and change-of-basis matrices between two representations $\rho_B$ and $\rho_{B'}$.

---

## Fundamental Theorem Matrix Representation

Let $T: V \to W$ be a linear transformation between finite-dimensional vector spaces, with ordered bases $B = \{v_1, \dots, v_n\}$ for $V$ and $C = \{w_1, \dots, w_m\}$ for $W$. Every vector $v \in V$ has a unique coordinate representation $[v]_B \in \mathbb{R}^n$, and every $T$ has a unique matrix representation $[T]_C^B$, an $m \times n$ matrix whose $j$-th column is $[T(v_j)]_C$. The Fundamental Theorem of Matrix Representation states:
$$[T(v)]_C = [T]_C^B \, [v]_B.$$

In words: to compute $T(v)$, you may instead coordinatize $v$ into a column vector, multiply by the matrix $[T]_C^B$, and interpret the resulting column vector as coordinates in $C$. This converts an abstract linear map — which might act on polynomials, functions, or matrices — into ordinary matrix-vector multiplication.

**Worked example.** Let $T: P_2 \to P_1$ be differentiation, $T(p) = p'$, with basis $B = \{1, x, x^2\}$ for $P_2$ and $C = \{1, x\}$ for $P_1$. Compute $T(1) = 0$, $T(x) = 1$, $T(x^2) = 2x$, and coordinatize each in $C$: $[0]_C = \binom{0}{0}$, $[1]_C = \binom{1}{0}$, $[2x]_C = \binom{0}{2}$. Stack these as columns:
$$[T]_C^B = \begin{pmatrix} 0 & 1 & 0 \\ 0 & 0 & 2 \end{pmatrix}.$$
Now take $p(x) = 3 + 2x - x^2$, so $[p]_B = (3, 2, -1)^T$. Then
$$[T]_C^B [p]_B = \begin{pmatrix} 0 & 1 & 0 \\ 0 & 0 & 2 \end{pmatrix}\begin{pmatrix} 3 \\ 2 \\ -1 \end{pmatrix} = \begin{pmatrix} 2 \\ -2 \end{pmatrix},$$
which un-coordinatizes to $2(1) + (-2)(x) = 2 - 2x$ — exactly $p'(x)$, confirming the theorem.

**Problem-solving application.** This theorem is what makes computing with linear transformations tractable: once you know $[T]_C^B$, applying $T$ to *any* vector reduces to a single matrix multiplication, without recomputing $T$ from its definition each time. It also explains why composition of linear maps corresponds to matrix multiplication ($[S \circ T] = [S][T]$) and why invertibility of $T$ corresponds to invertibility of $[T]_C^B$. In practice, when solving problems involving differential operators, rotations, or projections, the standard strategy is: build the matrix once from the basis vectors' images, then let matrix algebra — powers, inverses, eigenvalues — do the rest of the work.
```
