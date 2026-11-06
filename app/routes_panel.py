

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    request,
    url_for,
)

from .services import (
    dostepne_regiony,
    policz_wskazniki,
    raporty_roku,
    zapisz_raport,
)
from .validators import parametr_int

panel_bp = Blueprint("panel", __name__)

ROK_DOMYSLNY = 2026


@panel_bp.get("/")
def index():
    return "Panel wskaźników"


@panel_bp.get("/kpi")
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

    current_app.logger.info(
        "Obliczono wskaźniki dla regionu %s",
        w["region"],
    )

    return (
        f"<h1>Region: {w['region']}</h1>"
        f"<p>Marża: {w['marza']:.2%}</p>"
    )


@panel_bp.get("/regiony/<region:kod>")
def region(kod):
    regiony = dostepne_regiony(current_app.config["SCIEZKA_DANYCH"])

    if kod not in regiony:
        abort(404, description=f"Nieznany region: {kod}")

    liczba = policz_wskazniki(
        current_app.config["SCIEZKA_DANYCH"],
        kod,
    )["liczba_zamowien"]

    return f"<h1>Region {kod}</h1><p>Zamówień: {liczba}</p>"


@panel_bp.get("/raporty/", defaults={"rok": ROK_DOMYSLNY})
@panel_bp.get("/raporty/<int(min=2020, max=2030):rok>")
def raport(rok):
    liczba = len(raporty_roku(rok))
    return f"<h1>Raport {rok}</h1><p>Zapisane raporty: {liczba}</p>"


@panel_bp.route("/raporty/nowy", methods=["GET", "POST"])
def nowy_raport():
    if request.method == "GET":
        return """
        <h1>Nowy raport</h1>
        <form method="post">
            <label>Rok:
                <input name="rok">
            </label>
            <label>Region:
                <input name="region">
            </label>
            <button type="submit">Zapisz</button>
        </form>
        """

    try:
        rok = parametr_int(request.form.get("rok"), "rok")
    except ValueError as blad:
        abort(400, description=str(blad))

    region = request.form.get("region", "")

    if region not in dostepne_regiony(
        current_app.config["SCIEZKA_DANYCH"]
    ):
        abort(400, description=f"Nieznany region: {region}")

    if rok < 2020 or rok > 2030:
        abort(422, description="Rok musi być w zakresie 2020–2030")

    zapisz_raport(rok, region)

    if rok == ROK_DOMYSLNY:
        return redirect(url_for("panel.raport"), code=303)

    return redirect(url_for("panel.raport", rok=rok), code=303)


@panel_bp.get("/stary-panel")
def stary_panel():
    return redirect(url_for("panel.kpi"), code=301)
