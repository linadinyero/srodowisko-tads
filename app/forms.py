from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    InputRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


class FormularzBazowy(FlaskForm):
    class Meta:
        locales = ["pl"]


class FiltrForm(FormularzBazowy):
    region = SelectField(
        "Region",
        choices=[],
        validators=[Optional()],
    )
    rok = IntegerField(
        "Rok",
        validators=[
            Optional(),
            NumberRange(
                min=2020,
                max=2030,
                message="Zakres 2020-2030",
            ),
        ],
    )

    class Meta(FormularzBazowy.Meta):
        csrf = False


class RaportForm(FormularzBazowy):
    rok = IntegerField(
        "Rok",
        validators=[
            InputRequired(message="Pole jest wymagane"),
            NumberRange(
                min=2020,
                max=2030,
                message="Zakres 2020-2030",
            ),
        ],
    )
    region = SelectField(
        "Region",
        choices=[],
        validators=[InputRequired(message="Pole jest wymagane")],
    )
    szczegoly = BooleanField("Dołącz szczegóły")
    uwagi = TextAreaField(
        "Uwagi",
        validators=[
            Length(max=200, message="Najwyżej 200 znaków"),
        ],
    )
    zapisz = SubmitField("Zapisz raport")

    def __init__(self, istniejace=(), *args, **kwargs):
        self.istniejace = list(istniejace)
        super().__init__(*args, **kwargs)

    def validate_rok(self, field):
        if (field.data, self.region.data) in self.istniejace:
            raise ValidationError(
                "Raport za ten rok i region już istnieje"
            )


class ZbiorForm(FormularzBazowy):
    plik = FileField(
        "Plik CSV",
        validators=[
            FileRequired(message="Wskaż plik do wczytania"),
            FileAllowed(
                ["csv"],
                message="Dopuszczalny jest wyłącznie format CSV",
            ),
        ],
    )
    wczytaj = SubmitField("Wczytaj plik")