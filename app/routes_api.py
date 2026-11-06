

from flask import Blueprint, abort, current_app, request

from .services import (
    dostepne_regiony,
    policz_wskazniki,
    zapisz_raport,
)
from .validators import parametr_int

api_bp = Blueprint("api", __name__)


@api_bp.get("/kpi")
def kpi():
    region = request.args.get("region")

    if region is not None and region not in dostepne_regiony(
        current_app.config["SCIEZKA_DANYCH"]
    ):
        abort(404, description=f"Nieznany region: {region}")

    return policz_wskazniki(
        current_app.config["SCIEZKA_DANYCH"],
        region,
    )


@api_bp.route("/raporty", methods=["GET", "POST"])
def raporty():
    try:
        rok = parametr_int(request.args.get("rok"), "rok")
    except ValueError as blad:
        abort(400, description=str(blad))

    region = request.args.get("region", "PL")

    if region not in dostepne_regiony(
        current_app.config["SCIEZKA_DANYCH"]
    ):
        abort(400, description=f"Nieznany region: {region}")

    if rok < 2020 or rok > 2030:
        abort(422, description="Rok musi być w zakresie 2020–2030")

    if request.method == "POST":
        zapisz_raport(rok, region)

    return zapisz_raport(rok, region) if request.method == "GET" else {
        "rok": rok,
        "region": region,
    }
