import csv


def wczytaj_zamowienia(sciezka):
    with open(sciezka, newline="", encoding="utf-8") as plik:
        return list(csv.DictReader(plik))


def dostepne_regiony(sciezka):
    zamowienia = wczytaj_zamowienia(sciezka)
    regiony = {zamowienie["region"] for zamowienie in zamowienia}
    return sorted(regiony)


def policz_wskazniki(sciezka, region=None):
    zamowienia = wczytaj_zamowienia(sciezka)

    if region is not None:
        zamowienia = [
            zamowienie
            for zamowienie in zamowienia
            if zamowienie["region"] == region
        ]

    przychod = sum(float(zamowienie["przychod"]) for zamowienie in zamowienia)
    koszt = sum(float(zamowienie["koszt"]) for zamowienie in zamowienia)
    liczba_zamowien = len(zamowienia)

    if przychod == 0:
        marza = 0.0
    else:
        marza = round((przychod - koszt) / przychod, 4)

    return {
        "region": region,
        "liczba_zamowien": liczba_zamowien,
        "przychod": przychod,
        "koszt": koszt,
        "marza": marza,
    }