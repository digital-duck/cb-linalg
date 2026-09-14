# SPL Run: build_concept_book

- **Adapter:** claude_cli
- **Model:** claude-sonnet-5
- **Tokens:** 2528 in / 2177 out
- **Latency:** 37626ms
- **Timestamp:** 2026-09-14 05:03:55

## Output

```output


---

## Linear Equation

A linear equation relates variables using only two operations: multiplying each variable by a fixed constant, and adding the results together. In its general form with $n$ variables, it looks like

$$a_1x_1 + a_2x_2 + \dots + a_nx_n = b,$$

where the $a_i$ (coefficients) and $b$ are known constants. No variable is squared, multiplied by another variable, placed under a root, or fed into a function like $\sin$ or $\log$. This restriction is what makes the equation "linear" — geometrically, it describes a straight line (two variables), a flat plane (three variables), or a flat hyperplane (more variables), never a curve.

**Worked example.** A rideshare driver earns a flat \$3 pickup fee plus \$1.25 per mile driven. If a trip earns \$18.50, how many miles was it? Let $x$ be miles driven:

$$1.25x + 3 = 18.50.$$

Subtract 3 from both sides: $1.25x = 15.50$. Divide by 1.25: $x = 12.4$ miles. The check confirms it: $1.25(12.4) + 3 = 15.5 + 3 = 18.5$. Notice the two operations used to isolate $x$ — subtraction and division — are simply the inverses of the operations that built the equation (addition and multiplication), which is always the strategy for solving a linear equation in one variable.

**Problem-solving application.** Linear equations become genuinely useful when several unknowns are linked by several such equations — a *linear system*. Suppose a bakery sells only muffins ($x$) and scones ($y$). On Monday it sold 40 items for \$150, with muffins at \$3 and scones at \$4.50:

$$x + y = 40, \qquad 3x + 4.5y = 150.$$

Solving the first equation for $x = 40 - y$ and substituting into the second gives $3(40-y) + 4.5y = 150$, or $120 + 1.5y = 150$, so $y = 20$ and $x = 20$. This substitution method — reducing a system to one equation in one unknown — generalizes to any number of linear equations and is the foundation of techniques like Gaussian elimination used in economics, engineering, and computer graphics whenever many quantities must simultaneously satisfy multiple linear constraints. Recognizing when a real-world relationship is linear (constant rate, no compounding or interaction effects) is often the hardest step; once identified, solving it is mechanical.

---

## System Of Linear Equations

A system of linear equations is a collection of $m$ linear equations sharing the same $n$ variables $x_1, x_2, \ldots, x_n$. Each equation has the form

$$a_1 x_1 + a_2 x_2 + \cdots + a_n x_n = b,$$

where the $a_i$ (coefficients) and $b$ (constant) are fixed numbers. "Linear" means every variable appears only to the first power and never multiplied by another variable — no $x^2$, no $xy$, no $\sqrt{x}$. A *solution* to the system is an assignment of values to $x_1, \ldots, x_n$ that satisfies every equation simultaneously.

**Worked example.** Consider two equations in two unknowns:

$$2x + y = 7$$
$$x - y = 2$$

Solve by elimination: adding the equations cancels $y$, giving $3x = 9$, so $x = 3$. Substituting back, $y = 7 - 2(3) = 1$. Check both equations: $2(3)+1=7$ ✓ and $3-1=2$ ✓. Geometrically, each equation is a line in the $xy$-plane, and the solution $(3,1)$ is their point of intersection.

**Problem-solving application.** Real systems rarely have just two variables, so hand elimination becomes impractical. Software instead collects the coefficients and constants into arrays and solves the system numerically — the same elimination idea, just automated to handle dozens or thousands of variables at once.

For example, a company blending three raw materials to meet target quantities of protein, fat, and fiber can express each nutritional constraint as one linear equation; solving the resulting $3\times 3$ system gives the exact amounts of each material needed. In code, this is a single call:

```python
import numpy as np
A = np.array([[2, 1], [1, -1]])
b = np.array([7, 2])
x = np.linalg.solve(A, b)   # array([3., 1.])
```

A system may have exactly one solution (consistent and independent), infinitely many (consistent but dependent, e.g., two equations describing the same line), or none (inconsistent, e.g., parallel lines). Recognizing which case applies is the practical skill that underlies applications from circuit analysis to economic modeling — and it's exactly what a solver like `np.linalg.solve` checks internally before returning an answer.

---

## Solution Set

A system of equations places several constraints on the same variables at once. A **solution** is an ordered list of values — one for each variable — that satisfies *every* equation in the system simultaneously, not just one of them. The **solution set** is the collection of all such lists. Depending on the system, this set might contain exactly one solution, no solutions at all, or infinitely many.

**Worked example.** Consider the system
$$
\begin{aligned}
x + y &= 10 \\
2x - y &= 2
\end{aligned}
$$
A single equation like $x+y=10$ has infinitely many solutions on its own — $(4,6)$, $(7,3)$, $(0,10)$, and so on. But we need pairs $(x,y)$ that work in *both* equations. Adding the two equations eliminates $y$: $3x = 12$, so $x=4$. Substituting back gives $y=6$. Checking: $4+6=10$ ✓ and $2(4)-6=2$ ✓. The solution set here is a single ordered pair, written $\{(4,6)\}$. Geometrically, each equation is a line, and $(4,6)$ is the one point where the two lines cross.

**Problem-solving application.** The size of a solution set tells you something important about the system before you even finish solving it. Two lines in a plane either cross once (one solution), never cross because they're parallel (no solution, or the *empty set* $\varnothing$), or lie exactly on top of each other (infinitely many solutions). This matters in practice: if you're modeling a real situation — say, two companies' pricing plans as functions of usage — and you solve the system to find where costs are equal, an empty solution set tells you the plans *never* cost the same, while infinitely many solutions would mean the plans are identical for every amount of usage.

When working with larger systems (three or more variables), the same logic scales up: a solution is now a longer ordered list, such as $(x,y,z) = (1,-2,5)$, and you verify it the same way — plug it into *every* equation and confirm all are true. Before trusting an answer, always check it against each original equation; a value that satisfies one equation but not another is not part of the solution set, no matter how it was derived.
```
