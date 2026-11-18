
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
from werkzeug.utils import secure_filename

from .forms import FiltrForm, RaportForm, ZbiorForm
from .services import (
    dostepne_regiony,
    policz_wskazniki,
    raporty_roku,
    zapisz_raport,
    zestawienie_regionow,
    wykaz_raportow,
    wczytaj_zbior,
)
from .validators import parametr_int


panel_bp = Blueprint("panel", __name__)
ROK_DOMYSLNY = 2026


@panel_bp.get("/")
def index():
    return "Panel wskaźników"


@panel_bp.get("/kpi")
def kpi():
    sciezka = current_app.config["SCIEZKA_DANYCH"]
    regiony = dostepne_regiony(sciezka)

    formularz = FiltrForm(request.args)
    formularz.region.choices = [("", "wszystkie")] + [
        (region, region) for region in regiony
    ]

    region = None
    rok = None

    if formularz.validate():
        region = formularz.region.data or None
        rok = formularz.rok.data
    elif request.args:
        flash(
            "Kryteria zawężenia zostały pominięte",
            "ostrzezenie",
        )

    wskazniki = policz_wskazniki(sciezka, region, rok)

    current_app.logger.info(
        "Obliczono wskaźniki dla regionu %s",
        wskazniki["region"],
    )

    return render_template(
        "panel.html",
        wskazniki=wskazniki,
        zestawienie=zestawienie_regionow(sciezka),
        dzisiaj=date.today(),
        formularz=formularz,
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
    sciezka = current_app.config["SCIEZKA_DANYCH"]
    regiony = dostepne_regiony(sciezka)

    istniejace = [
        (raport["rok"], raport["region"])
        for raport in wykaz_raportow()
    ]

    formularz = RaportForm(istniejace=istniejace)
    formularz.region.choices = [
        ("", "Wybierz region")
    ] + [(region, region) for region in regiony]

    if formularz.validate_on_submit():
        rok = formularz.rok.data
        region = formularz.region.data
        uwagi = formularz.uwagi.data or ""

        zapisz_raport(rok, region, uwagi)
        flash(f"Raport za rok {rok} zapisany", "success")

        return redirect(
            url_for("panel.raport", rok=rok),
            code=303,
        )

    status = 422 if formularz.errors else 200

    return render_template(
        "new_report.html",
        formularz=formularz,
    ), status


@panel_bp.route("/wczytaj", methods=["GET", "POST"])
def wczytaj():
    formularz = ZbiorForm()

    if formularz.validate_on_submit():
        plik = formularz.plik.data
        nazwa = secure_filename(plik.filename)

        try:
            liczba = wczytaj_zbior(plik.stream)
        except ValueError as blad:
            formularz.plik.errors.append(
                f"Niepoprawna zawartość: {blad}"
            )
        else:
            flash(
                f"Wczytano {liczba} zamówień z pliku {nazwa}",
                "success",
            )
            return redirect(url_for("panel.wczytaj"), 303)

    status = 422 if formularz.errors else 200

    return render_template(
        "upload.html",
        formularz=formularz,
    ), status


@panel_bp.get("/stary-panel")
def stary_panel():
    return redirect(url_for("panel.kpi"), code=301)
