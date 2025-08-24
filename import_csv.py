import csv

def lade_bool_matrix_aus_csv_und_dedupliziere_zeilen(pfad):
    """
    Liest eine CSV-Datei ein, wandelt sie in eine 0/1-Matrix um und entfernt doppelte Zeilen.
    Gibt die deduplizierte Matrix zurück.
    """
    matrix = []
    max_len = 0
    # Erstes Einlesen, um maximale Spaltenzahl zu bestimmen
    with open(pfad, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        rows = list(reader)
        max_len = max(len(row) for row in rows)
    # Umwandlung und Auffüllen
    for row in rows:
        row += [''] * (max_len - len(row))
        neue_zeile = []
        for wert in row:
            if str(wert).strip().lower() in ('', 'false', '0', 'none'):
                neue_zeile.append(0)
            else:
                neue_zeile.append(1)
        matrix.append(tuple(neue_zeile))  # tuple für Set-Vergleich

    # Zeilen deduplizieren
    unique_rows = list(dict.fromkeys(matrix))  # Reihenfolge bleibt erhalten

    # Zurück zu Listen
    return [list(row) for row in unique_rows]