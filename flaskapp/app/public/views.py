# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user, current_user

from app.decorators import anonymous_required
from app.extensions import login_manager
#from app.public.forms import LoginForm
#from app.user.forms import RegisterForm
from app.models import *
from app.utils import sync_cart, get_current_cart

public = Blueprint("public", __name__, static_folder="../static")



@public.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
    nav_menu = NavMenu.query.all()
    slideshows = SlideShowImage.query.all()
    hometext = HomeText.query.first()
    call_to_action = CallToAction.query.first()
    logo = Logo.query.first()
    techno_img = TechnologiesImage.query.all()
    text_techno = TechnologiesText.query.first()
    footer_text = FooterText.query.all()
    tracking_script = TrackingScript.query.all()
    media_icons = SocialMediaIcon.query.all()
    footer_image = FooterImage.query.first()
    copyright_text = CopyRight.query.first()
    background_image = BackgroundImage.query.first()
    favicon_image = FaviconImage.query.first()
    brand = BrandName.query.first()
    seo = Seo.query.first()
    return render_template("public/home.html", footer_image=footer_image, icons=media_icons,
                           footer_text=footer_text, slideshows=slideshows,
                           home_title=hometext, logo=logo, techno_img=techno_img,
                           text_techno=text_techno, copyright_text=copyright_text,
                           background_image=background_image, call_to_action=call_to_action,
                           nav_menu=nav_menu, brand=brand, seo=seo,
                           favicon_image=favicon_image, tracking_script=tracking_script)


@public.route('/under_construction')
def under_construction():
    logo = Logo.query.first()
    footer_text = FooterText.query.all()
    media_icons = SocialMediaIcon.query.all()
    footer_image = FooterImage.query.first()
    copyright_text = CopyRight.query.first()
    return render_template("public/undre_construction.html", logo=logo, footer_text=footer_text, footer_image=footer_image, icons=media_icons, copyright_text=copyright_text)



@public.route('/product/<int:product_id>/<product_name>')
def view_product(product_id, product_name):
    product = Module.query.get_or_404(product_id)
    return render_template("public/product.html", product=product)


@public.route("/about/")
def about():
    """About page."""
    footer_text = FooterText.query.all()
    media_icons = SocialMediaIcon.query.all()
    footer_image = FooterImage.query.first()
    copyright_text = CopyRight.query.first()
    return render_template("public/about.html", logo = Logo.query.first(), footer_text=footer_text, footer_image=footer_image, icons=media_icons, copyright_text=copyright_text)




@public.route('/cart/')
def cart_details():
    cart = get_current_cart()
    logo = Logo.query.first()
    footer_text = FooterText.query.all()
    media_icons = SocialMediaIcon.query.all()
    footer_image = FooterImage.query.first()
    copyright_text = CopyRight.query.first()
    return render_template('public/cart/view.html', cart=cart, logo=logo, footer_text=footer_text, footer_image=footer_image, icons=media_icons, copyright_text=copyright_text)


@public.route('/download/')
def download():
    if current_user.is_authenticated:
        return redirect(url_for('client.download'))
    logo = Logo.query.first()
    footer_text = FooterText.query.all()
    media_icons = SocialMediaIcon.query.all()
    footer_image = FooterImage.query.first()
    copyright_text = CopyRight.query.first()
    return render_template('public/download.html', logo=logo, footer_text=footer_text, footer_image=footer_image, icons=media_icons, copyright_text=copyright_text)
