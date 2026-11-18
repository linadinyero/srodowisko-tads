

def parametr_int(wartosc, nazwa="rok"):
    if wartosc is None or wartosc == "":
        raise ValueError(f"Brak wymaganego parametru: {nazwa}")

    try:
        return int(wartosc)
    except (TypeError, ValueError):
        raise ValueError(
            f"Parametr {nazwa} musi być liczbą całkowitą"
        )
