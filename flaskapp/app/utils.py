from flask import url_for, redirect
from wtforms.fields import Field
from wtforms.widgets import HiddenInput
from wtforms.compat import text_type


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField
        return isinstance(field, HiddenField)

    app.add_template_global(index_for_role)


def index_for_role(role):
    return url_for(role.index)


class CustomSelectField(Field):
    widget = HiddenInput()

    def __init__(self, label='', validators=None, multiple=False,
                 choices=[], allow_custom=True, **kwargs):
        super(CustomSelectField, self).__init__(label, validators, **kwargs)
        self.multiple = multiple
        self.choices = choices
        self.allow_custom = allow_custom

    def _value(self):
        return text_type(self.data) if self.data is not None else ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[1]
            self.raw_data = [valuelist[1]]
        else:
            self.data = ''


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


def put_session_cart_id():
    try:
        session['cart_id']
    except:
        u = uuid.uuid4()
        user_agent = request.headers.get('User-Agent')
        if user_agent is not None:
            user_agent = user_agent.encode('utf-8')
        base = 'cart: {0}|{1}|{2}'.format(_get_remote_addr(), user_agent, u)
        if str is bytes:
            base = text_type(base, 'utf-8', errors='replace')  # pragma: no cover
        h = sha512()
        h.update(base.encode('utf8'))
        session['cart_id'] = h.hexdigest()


def sync_cart():
    from app.models import Cart

    user_cart = Cart.query.filter_by(user_id=current_user.id).order_by(Cart.id.desc()).first()
    if user_cart:
        Cart.query.filter_by(user_id=current_user.id).filter(Cart.id != user_cart.id).delete()
    else:
        session_id = session['cart_id']
        cart = Cart.query.filter_by(session_id=session_id).order_by(Cart.id.desc()).first()
        if cart:
            Cart.query.filter_by(session_id=session_id).filter(Cart.id != cart.id).delete()
            cart.user_id = current_user.id
            db.session.add(cart)
            db.session.commit()


def get_current_cart():
    from app.models import Cart

    session_id = session['cart_id']
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            Cart.query.filter_by(user_id=current_user.id).filter(Cart.id != cart.id).delete()
        else:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
            db.session.refresh(cart)
    else:
        cart = Cart.query.filter_by(session_id=session_id).first()
        if cart:
            Cart.query.filter_by(session_id=session_id).filter(Cart.id != cart.id).delete()
        else:
            cart = Cart(session_id=session_id)
            db.session.add(cart)
            db.session.commit()
            db.session.refresh(cart)

    return cart


def get_setting_val(setting):
    if type(()) != type(setting):
        return None
    if len(setting) < 2:
        return None
    setting_obj = Setting.query.filter_by(name=setting[0]).first()
    if not setting_obj:
        setting_obj = Setting.create(
            name=setting[0],
            display_name=setting[1],
            value=''
        )
        db.session.add(setting_obj)
        db.session.commit()
    return setting_obj


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"
