from flask import Blueprint, abort, current_app, jsonify, request

from .services import dostepne_regiony, policz_wskazniki


api_bp = Blueprint("api", __name__)


@api_bp.get("/kpi")
def kpi():
    region = request.args.get("region")

    if region is not None and region not in dostepne_regiony(
        current_app.config["SCIEZKA_DANYCH"]
    ):
        abort(404, description=f"Nieznany region: {region}")

    w = policz_wskazniki(
        current_app.config["SCIEZKA_DANYCH"],
        region,
    )

    return jsonify(w)
