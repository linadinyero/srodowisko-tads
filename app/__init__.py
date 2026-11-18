import logging
import time
from datetime import date

from flask import Flask, jsonify, request, render_template
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import HTTPException

from .config import KONFIGURACJE
from .converters import RegionConverter
from .filters import zarejestruj_filtry
from .services import dostepne_regiony


csrf = CSRFProtect()


def create_app(nazwa_konfiguracji="rozwojowa"):
    app = Flask(__name__)
    app.config.from_object(KONFIGURACJE[nazwa_konfiguracji])
    app.logger.setLevel(logging.INFO)
    app.url_map.converters["region"] = RegionConverter

    csrf.init_app(app)

    zarejestruj_filtry(app)

    @app.context_processor
    def dane_wspolne():
        return {
            "regiony": dostepne_regiony(app.config["SCIEZKA_DANYCH"]),
            "rok_biezacy": date.today().year,
        }

    @app.before_request
    def rozpocznij_pomiar():
        request.czas_start = time.perf_counter()
    
    @app.after_request
    def dodaj_czas_odpowiedzi(odpowiedz):
        czas_start = getattr(request, "czas_start", None)

        if czas_start is None:
            czas = 0
        else:
            czas = (time.perf_counter() - czas_start) * 1000

        odpowiedz.headers["X-Czas-Ms"] = f"{czas:.2f}"
        return odpowiedz

    @app.errorhandler(HTTPException)
    def obsluz_blad(blad):
        if blad.code == 308:
            return blad

        if request.path.startswith("/api/"):
            odpowiedz = jsonify({
                "blad": blad.description,
                "kod": blad.code
            })
            odpowiedz.status_code = blad.code
            return odpowiedz

        return render_template(
            "errors/error.html",
            kod=blad.code,
            opis=blad.description
        ), blad.code

    from .routes_api import api_bp
    from .routes_panel import panel_bp

    app.register_blueprint(panel_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(api_bp, url_prefix="/api/v2", name="api_v2")

    return app