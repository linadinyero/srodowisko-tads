
import csv

_RAPORTY = []


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
            zamowienie for zamowienie in zamowienia
            if zamowienie["region"] == region
        ]

    przychod = sum(float(z["przychod"]) for z in zamowienia)
    koszt = sum(float(z["koszt"]) for z in zamowienia)
    liczba_zamowien = len(zamowienia)

    marza = 0.0 if przychod == 0 else round(
        (przychod - koszt) / przychod, 4
    )

    return {
        "region": region,
        "liczba_zamowien": liczba_zamowien,
        "przychod": przychod,
        "koszt": koszt,
        "marza": marza,
    }


def zapisz_raport(rok, region):
    raport = {"rok": rok, "region": region}
    _RAPORTY.append(raport)
    return raport


def raporty_roku(rok):
    return [
        raport for raport in _RAPORTY
        if raport["rok"] == rok
    ]
