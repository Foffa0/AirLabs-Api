from functools import wraps

from flask import flash, render_template
from flask_login import current_user


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return render_template('public/activate_account.html')
        return func(*args, **kwargs)

    return decorated_function