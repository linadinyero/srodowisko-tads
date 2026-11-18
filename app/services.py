
import csv
import io

_RAPORTY = []

WYMAGANE_KOLUMNY = {"data", "region", "przychod", "koszt"}


def wczytaj_zamowienia(sciezka):
    with open(sciezka, newline="", encoding="utf-8") as plik:
        return list(csv.DictReader(plik))


def wczytaj_zbior(strumien):
    try:
        zawartosc = strumien.read().decode("utf-8")
    except UnicodeDecodeError as blad:
        raise ValueError("plik nie jest poprawnym tekstem UTF-8") from blad

    czytnik = csv.DictReader(io.StringIO(zawartosc))

    kolumny = set(czytnik.fieldnames or [])
    brakujace = sorted(WYMAGANE_KOLUMNY - kolumny)

    if brakujace:
        raise ValueError(f"brak kolumn: {', '.join(brakujace)}")

    return sum(1 for _ in czytnik)


def dostepne_regiony(sciezka):
    zamowienia = wczytaj_zamowienia(sciezka)
    regiony = {zamowienie["region"] for zamowienie in zamowienia}
    return sorted(regiony)


def policz_wskazniki(sciezka, region=None, rok=None):
    zamowienia = wczytaj_zamowienia(sciezka)

    if region is not None:
        zamowienia = [
            zamowienie for zamowienie in zamowienia
            if zamowienie["region"] == region
        ]

    if rok is not None:
        zamowienia = [
            zamowienie for zamowienie in zamowienia
            if zamowienie["data"].startswith(str(rok))
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


def zapisz_raport(rok, region, uwagi=""):
    raport = {
        "rok": rok,
        "region": region,
        "uwagi": uwagi,
    }
    _RAPORTY.append(raport)
    return raport


def raporty_roku(rok):
    return [
        raport for raport in _RAPORTY
        if raport["rok"] == rok
    ]


def wykaz_raportow():
    return list(_RAPORTY)


def zestawienie_regionow(sciezka):
    return [
        policz_wskazniki(sciezka, region)
        for region in dostepne_regiony(sciezka)
    ]
