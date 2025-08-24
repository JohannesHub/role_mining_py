Alles klar — hier ist eine **exakte ILP-Formulierung** fürs Role Mining mit Ziel *„#Rollen minimieren“*. Du kannst sie 1:1 in einen MIP-Solver (Gurobi, CBC, OR-Tools, CPLEX) kippen.

## Setup

* Mengen:
  $U$ Nutzer, $P$ Berechtigungen, $K$ maximale Rollenanzahl (Upper Bound, z. B. $\min(|U|,|P|)$).
* Gegeben: Binärmatrix $A\in\{0,1\}^{|U|\times|P|}$ (UPA).

## Variablen

* $x_{u r}\in\{0,1\}$: Nutzer $u$ bekommt Rolle $r$
* $y_{r p}\in\{0,1\}$: Rolle $r$ enthält Permission $p$
* $z_{r}\in\{0,1\}$: Rolle $r$ wird genutzt
* $w_{u r p}\in\{0,1\}$: „AND“-Hilfsvariable für $x_{u r}\land y_{r p}$

## Ziel

$$
\min \sum_{r=1}^{K} z_r
$$

## Nebenbedingungen

**Aktivierungs-Links**

$$
x_{u r}\le z_r,\quad y_{r p}\le z_r \quad \forall u,r,p
$$

**Linearisiere $w_{u r p}=x_{u r}\land y_{r p}$**

$$
\begin{aligned}
&w_{u r p}\le x_{u r}\\
&w_{u r p}\le y_{r p}\\
&w_{u r p}\ge x_{u r}+y_{r p}-1
\end{aligned}
\quad \forall u,r,p
$$

**Exakte Rekonstruktion von $A$**

* Für Einsen: Jede $1$ in $A$ muss von mind. einer Rolle „erklärt“ werden:

$$
\sum_{r=1}^{K} w_{u r p}\ge 1 \quad \forall (u,p)\ \text{mit}\ A_{u p}=1
$$

* Für Nullen: Keine Überdeckung zulassen:

$$
\sum_{r=1}^{K} w_{u r p}=0 \quad \forall (u,p)\ \text{mit}\ A_{u p}=0
$$

**Sauberkeit / optionale Stärkung**

$$
\begin{aligned}
&z_r \le \sum_u x_{u r},\qquad z_r \le \sum_p y_{r p} && \text{(keine leeren Rollen)}\\
&z_{r}\ge z_{r+1} && \text{(Symmetrieabbau, optional)}
\end{aligned}
$$

Das war’s: Diese ILP liefert **exakt** eine Faktorisierung $A = X\;\text{(bool)}\;Y$ und minimiert die Anzahl genutzter Rollen $\sum z_r$.

---

## Mini-Template in Python (PuLP/CBC)

```python
import pulp as pl
U, P = range(n_users), range(n_perms)
K = min(len(U), len(P))  # simple upper bound
A = ...  # 0/1 list of lists: A[u][p]

# Vars
x = pl.LpVariable.dicts('x', (U, range(K)), 0, 1, cat='Binary')
y = pl.LpVariable.dicts('y', (range(K), P), 0, 1, cat='Binary')
z = pl.LpVariable.dicts('z', range(K), 0, 1, cat='Binary')
w = pl.LpVariable.dicts('w', (U, range(K), P), 0, 1, cat='Binary')

m = pl.LpProblem('ExactRoleMining', pl.LpMinimize)
m += pl.lpSum(z[r] for r in range(K))

# Linking
for u in U:
    for r in range(K):
        m += x[u][r] <= z[r]
for r in range(K):
    for p in P:
        m += y[r][p] <= z[r]

# AND linearization
for u in U:
    for r in range(K):
        for p in P:
            m += w[u][r][p] <= x[u][r]
            m += w[u][r][p] <= y[r][p]
            m += w[u][r][p] >= x[u][r] + y[r][p] - 1

# Exact reconstruction
for u in U:
    for p in P:
        if A[u][p] == 1:
            m += pl.lpSum(w[u][r][p] for r in range(K)) >= 1
        else:
            m += pl.lpSum(w[u][r][p] for r in range(K)) == 0

# Optional strengthening
for r in range(K-1):
    m += z[r] >= z[r+1]

m.solve(pl.PULP_CBC_CMD(msg=True))
# Auslesen: aktive Rollen = [r for r in range(K) if pl.value(z[r]) > 0.5]
```

### Praktische Tipps (kurz)

* **K kleiner machen:** Starte mit kleinem $K$ und erhöhe nur bei Infeasibility.
* **Preprocessing:** Entferne identische Nutzer/Permissions, dominiert/inkludierte Spalten/Zeilen.
* **Symmetrie:** Obige Ordnung auf $z$ hilft, ggf. zusätzlich Reihenfolge auf $y$ (lex-Constraints) einziehen.
* **Skalierung:** Das $w$-Tensor hat Größe $|U|\cdot K\cdot|P|$. Für große Instanzen Kandidatenrollen vorab generieren (z. B. häufige Permission-Sets) und $K$ = #Kandidaten setzen – dann sparst du massiv Variablen.

Wenn du willst, baue ich dir das Template auf deine Daten (CSV → Lösung) um.
