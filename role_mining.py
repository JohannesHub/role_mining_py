import random
import pulp as pl
from import_csv import lade_bool_matrix_aus_csv_und_dedupliziere_zeilen

#TODOs
#mit nicht binärdaten umgehen
#zuweisung rollen zu user finden

# --- Daten generieren ---
A = lade_bool_matrix_aus_csv_und_dedupliziere_zeilen("daten2.csv")
print("Eingelesene Matrix (A):")
for row in A:
    print(row)

n_users = len(A)
n_perms = len(A[0])

# --- ILP Setup ---
U, P = range(n_users), range(n_perms)
K = min(n_users, n_perms)  # maximal so viele Rollen wie Nutzer oder Berechtigungen

x = pl.LpVariable.dicts('x', (U, range(K)), 0, 1, cat='Binary')
y = pl.LpVariable.dicts('y', (range(K), P), 0, 1, cat='Binary')
z = pl.LpVariable.dicts('z', range(K), 0, 1, cat='Binary')
w = pl.LpVariable.dicts('w', (U, range(K), P), 0, 1, cat='Binary')

m = pl.LpProblem('ExactRoleMining', pl.LpMinimize)

# Ziel: Minimale Anzahl Rollen
m += pl.lpSum(z[r] for r in range(K))

# --- Constraints ---
# Link x,y mit z
for u in U:
    for r in range(K):
        m += x[u][r] <= z[r]
for r in range(K):
    for p in P:
        m += y[r][p] <= z[r]

# Linearisiere w = x AND y
for u in U:
    for r in range(K):
        for p in P:
            m += w[u][r][p] <= x[u][r]
            m += w[u][r][p] <= y[r][p]
            m += w[u][r][p] >= x[u][r] + y[r][p] - 1

# Exakte Rekonstruktion
for u in U:
    for p in P:
        if A[u][p] == 1:
            m += pl.lpSum(w[u][r][p] for r in range(K)) >= 1
        else:
            m += pl.lpSum(w[u][r][p] for r in range(K)) == 0

# Symmetrieabbau
for r in range(K-1):
    m += z[r] >= z[r+1]

# --- Lösen ---
m.solve(pl.PULP_CBC_CMD(msg=True))

# --- Ergebnisse ---
active_roles = [r for r in range(K) if pl.value(z[r]) > 0.5]
print("Optimale Anzahl Rollen:", len(active_roles))
print("Aktive Rollen IDs:", active_roles)

# Beispielausgabe: welche Permissions in Rolle 0 sind
for r in active_roles:
    perms = [p for p in P if pl.value(y[r][p]) > 0.5]
    print(f"Rolle {r} enthält Permissions {perms}")
