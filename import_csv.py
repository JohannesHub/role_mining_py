import csv
from collections import defaultdict

def lade_bool_matrizen_gruppiert_nach_masterid(pfad):
    """
    Liest eine CSV-Datei mit Header ein, gruppiert die Zeilen nach Master-ID (erstes Feld).
    Jede Gruppe wird in eine eigene 0/1-Matrix umgewandelt (ohne doppelte Zeilen).
    Zeilen ohne Master-ID werden ignoriert.
    Gibt eine Liste von Matrizen zurück.
    """
    gruppen = defaultdict(list)
    max_len = 0

    with open(pfad, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        header = next(reader, None)  # Header überspringen
        for row in reader:
            if not row or not row[0].strip():
                continue  # Zeile ohne Master-ID ignorieren
            max_len = max(max_len, len(row))
            gruppen[row[0]].append(row)

    matrizen = []
    for rows in gruppen.values():
        matrix = []
        for row in rows:
            row += [''] * (max_len - len(row))
            neue_zeile = []
            for wert in row:
                if str(wert).strip().lower() in ('', 'false', '0', 'none'):
                    neue_zeile.append(0)
                else:
                    neue_zeile.append(1)
            matrix.append(tuple(neue_zeile))
        # Zeilen deduplizieren
        unique_rows = list(dict.fromkeys(matrix))
        matrizen.append([list(row) for row in unique_rows])
    return matrizen