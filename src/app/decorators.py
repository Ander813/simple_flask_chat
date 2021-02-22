from functools import wraps

from flask import url_for
from flask_login import current_user
from werkzeug.local import LocalProxy
from flask import redirect


def logged_in_redirect(url):
    """
    redirects user if he is already logged in
    """

    def redirect_to(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_anonymous:
                return redirect(url_for(url))
            else:
                return func(*args, **kwargs)

        return wrapper

    return redirect_to
