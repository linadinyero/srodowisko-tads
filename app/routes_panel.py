
from datetime import date

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from .services import (
    dostepne_regiony,
    policz_wskazniki,
    raporty_roku,
    zapisz_raport,
    zestawienie_regionow,
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
    sciezka = current_app.config["SCIEZKA_DANYCH"]
    regiony = dostepne_regiony(sciezka)

    if region is not None and region not in regiony:
        abort(404, description=f"Nieznany region: {region}")

    wskazniki = policz_wskazniki(sciezka, region)

    current_app.logger.info(
        "Obliczono wskaźniki dla regionu %s",
        wskazniki["region"],
    )

    return render_template(
        "panel.html",
        wskazniki=wskazniki,
        zestawienie=zestawienie_regionow(sciezka),
        dzisiaj=date.today(),
    )


@panel_bp.get("/regiony/<region:kod>")
def region(kod):
    sciezka = current_app.config["SCIEZKA_DANYCH"]
    regiony = dostepne_regiony(sciezka)

    if kod not in regiony:
        abort(404, description=f"Nieznany region: {kod}")

    wskazniki = policz_wskazniki(sciezka, kod)

    return render_template(
        "panel.html",
        wskazniki=wskazniki,
        zestawienie=zestawienie_regionow(sciezka),
        dzisiaj=date.today(),
    )


@panel_bp.get("/raporty/", defaults={"rok": ROK_DOMYSLNY})
@panel_bp.get("/raporty/<int(min=2020, max=2030):rok>")
def raport(rok):
    return render_template(
        "report.html",
        rok=rok,
        zapisane=raporty_roku(rok),
    )



@panel_bp.route("/raporty/nowy", methods=["GET", "POST"])
def nowy_raport():
    if request.method == "GET":
        return """
        <form method="post">
            <label>Rok:
                <input name="rok" type="text">
            </label>
            <label>Region:
                <input name="region" type="text">
            </label>
            <button type="submit">Zapisz raport</button>
        </form>
        """

    try:
        rok = parametr_int(request.form.get("rok"), "rok")
    except (ValueError, TypeError):
        abort(400, description="Nieprawidłowy rok")

    region = request.form.get("region", "").strip()
    regiony = dostepne_regiony(current_app.config["SCIEZKA_DANYCH"])

    if region not in regiony:
        abort(400, description=f"Nieznany region: {region}")

    if not 2020 <= rok <= 2030:
        abort(422, description="Rok musi być z zakresu 2020–2030")

    zapisz_raport(rok, region)
    flash(f"Raport za rok {rok} został zapisany", "sukces")

    return redirect(
        url_for("panel.raport", rok=rok),
        code=303,
    )

@panel_bp.get("/stary-panel")
def stary_panel():
    return redirect(url_for("panel.kpi"), code=301)
