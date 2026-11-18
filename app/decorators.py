

from functools import wraps


def wymagany_parametr(nazwa):
    def dekorator(funkcja):
        @wraps(funkcja)
        def opakowanie(*args, **kwargs):
            from flask import abort, request

            if not request.args.get(nazwa):
                abort(400, description=f"Brak wymaganego parametru: {nazwa}")

            return funkcja(*args, **kwargs)

        return opakowanie

    return dekorator


