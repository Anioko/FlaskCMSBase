from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from flask_rq import get_queue
from flask_ckeditor import upload_success
from flask_sqlalchemy import Pagination

from app import db
#from app.admin.forms import (
    #ChangeAccountTypeForm,
    #ChangeUserEmailForm,
    #InviteUserForm,
    #NewUserForm,
#)
from app.decorators import admin_required
from app.email import send_email
from app.models import *
from app.admin.forms import *
admin = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')

@admin.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('upload')
    image_filename = images.save(f)
    url = url_for('_uploads.uploaded_file', setname='images',
                  filename=image_filename, _external=True)
    return upload_success(url=url)


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users')
@login_required
@admin_required
def registered_users():
    """View all registered users."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles)


@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'.format(
            user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'.format(
            user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/slideshows-list')
@login_required
@admin_required
def added_slideshows():
    """View all registered users."""
    slideshow = SlideShowImage.query.all()
    if slideshow is None:
        return redirect(url_for('admin.add_slideshows'))
    return render_template(
        'admin/slideshows/added_slideshows.html', slideshow=slideshow)

@admin.route('/slideshows/add_slideshow', methods=['GET', 'POST'])
@admin_required
def add_slideshow():
    form = SlideShowCrudForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            title = form.title.data
            image = images.save(request.files['image'])
            slideshow = SlideShowImage(title=title,image_filename=image)
            db.session.add(slideshow)
            db.session.commit()
            flash("SlideShow added successfully .", "success")
            return redirect(url_for("admin.added_slideshows"))
    
    return render_template("admin/slideshows/add_slideshow.html", form=form)

@admin.route('/slideshows/<int:slideshow_id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_slideshow(slideshow_id):
    """Delete the item """
    slideshows = SlideShowImage.query.filter_by(id=slideshow_id).first()
    db.session.commit()
    db.session.delete(slideshows)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_slideshows'))


@admin.route('/images-list')
@login_required
@admin_required
def added_images():
    """View all added images to the public area under the Information/Tech area."""
    images = TechnologiesImage.query.all()
    if images is None:
        return redirect(url_for('admin.add_image'))
    return render_template(
        'admin/images/added_images.html', slideshow=images)

@admin.route('/images/add_image', methods=['GET', 'POST'])
@admin_required
def add_image():
    form = ImageTechnologyForm()
    if request.method == 'POST':
        image = images.save(request.files['image'])
        technology_img = TechnologiesImage(image=image)
        db.session.add(technology_img)
        db.session.commit()
        flash("Technology Added Successfully .", "success")
        return redirect(url_for('admin.added_images'))
    return render_template("admin/images/add_image.html", form=form)

'''
##needless to edit the, just delete is enough
@admin.route('/images/<int:image_id>/edit', methods=['POST', 'GET'])
@admin_required
def edit_image(image_id):
    image_data = TechnologiesImage.query.get(image_id)
    form = ImageTechnologyForm(obj=image_data)
    form.image.validators = form.image.validators[1:]
    form.image.validators.insert(0, Optional())
    form.image.flags.required = False
    if request.method == 'POST':
        if request.files['image']:
            image = images.save(request.files['image'])
            if os.path.exists(image_data.image_path):
                os.remove(image_data.image_path)
            image_data.image_filename = image
        db.session.add(image_data)
        db.session.commit()
        flash("Technology Image Updated Successfully.", "success")
        return redirect(url_for("admin.technology_image"))
    return render_template("admin/images/edit_image.html", form=form, image_data=image_data)
'''
# delete image 
@admin.route('/images/delete/<int:image_id>', methods=['GET', 'POST'])
@admin_required
def delete_image(image_id):
    data = TechnologiesImage.query.get(image_id)
    db.session.delete(data)
    db.session.commit()
    flash("Technology Image deleted Successfully.", "success")
    return redirect(url_for('admin.added_images'))



@admin.route('/calltoaction-list')
@login_required
@admin_required
def added_calltoaction():
    """View all added call to actin text."""
    data = CallToAction.query.first()
    if data is None:
        return redirect(url_for('admin.add_call_to_action'))
    return render_template(
        'admin/calltoaction/added_calltoaction.html', data=data)

# Add CallToAction 
@admin.route('/calltaction/call_to_action', methods=['POST', 'GET'])
@admin_required
def add_call_to_action():
    form = CallToActionForm()
    if form.validate_on_submit():
        data = CallToAction(
            text=form.text.data,
            url=form.url.data
            )
        db.session.add(data)
        db.session.commit()
        flash("Call To Action Text Added Successfully.", "success")
        return redirect(url_for('admin.added_calltoaction'))
    return render_template('admin/calltoaction/add_call_to_action.html', form=form)

@admin.route('/calltoaction/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_calltoaction(id):
    """Delete the item """
    data = CallToAction.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_calltoaction'))


@admin.route('/nav-menu', methods=['GET', 'POST'])
@login_required
@admin_required
def nav_menu():
    """Create a new navigation menu."""
    item = NavMenu.query.first()
    if item is not None:
        return redirect(url_for('admin.added_navmenu'))
        
    form = NavMenuForm()
    if form.validate_on_submit():
        data = NavMenu(
            text=form.text.data,
            url=form.url.data)
        db.session.add(data)
        db.session.commit()
        flash('NavMenu {} successfully created'.format(data.text),
              'form-success')
        return redirect(url_for('admin.added_navmenu'))
    return render_template('admin/nav_menu.html', form=form)

@admin.route('/navmenu-list')
@login_required
@admin_required
def added_navmenu():
    """View all added navigations."""
    data = NavMenu.query.all()
    return render_template(
        'admin/added_navmenu.html', data=data)

@admin.route('/navmenu/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_navmenu(id):
    """Delete the item """
    data = NavMenu.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_navmenu'))

@admin.route('/hometext', methods=['GET', 'POST'])
@login_required
@admin_required
def home_text():
    """Create a new text for the home page."""
    item = HomeText.query.first()
    if item is not None:
        return redirect(url_for('admin.added_hometext'))
        
    form = HomeTextForm()
    if form.validate_on_submit():
        data = HomeText(
            firstext=form.firstext.data,
            secondtext=form.secondtext.data)
        db.session.add(data)
        db.session.commit()
        flash('HomeText {} successfully created'.format(data.firstext),
              'form-success')
        return redirect(url_for('admin.added_hometext'))
    return render_template('admin/hometext/add_hometext.html', form=form)

@admin.route('/hometext-list')
@login_required
@admin_required
def added_hometext():
    """View all added texts."""
    data = HomeText.query.first()
    return render_template(
        'admin/hometext/added_hometext.html', data=data)

@admin.route('/hometext/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_hometext(id):
    """Delete the home text """
    data = HomeText.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.home_text'))


@admin.route('/information-list')
@login_required
@admin_required
def added_information():
    """View all added call to actin text."""
    data = TechnologiesText.query.all()
    if data is None:
        return redirect(url_for('admin.add_information'))
    return render_template(
        'admin/information/added_information.html', data=data)

# Add Information to Public Page
@admin.route('/information/add', methods=['POST', 'GET'])
@admin_required
def add_information():
    form = TechnologiesForm()
    if form.validate_on_submit():
        data = TechnologiesText(
            firstext = form.firstext.data,
            secondtext = form.secondtext.data
            )
        db.session.add(data)
        db.session.commit()
        flash("Text Added Successfully.", "success")
        return redirect(url_for('admin.added_information'))
    return render_template('admin/information/add_information.html', form=form)

@admin.route('/information/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_information(id):
    """Delete the information added """
    data = TechnologiesText.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    if data is None:
        return redirect(url_for('admin.add_information'))
    return redirect(url_for('admin.added_information'))

@admin.route('/background-image')
@login_required
@admin_required
def added_background_image():
    """View available background image"""
    data = BackgroundImage.query.first()
    if data is None:
        return redirect(url_for('admin.add_background_image'))
    return render_template(
        'admin/background/added_images.html', data=data)

# Background Image add method
@admin.route('/background_image/add', methods=['POST', 'GET'])
@admin_required
def add_background_image():
    form = BackgroundImageForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['background_image'])
        background_image = BackgroundImage(background_image=image)
        db.session.add(background_image)
        db.session.commit()
        flash("Background Added Successfully .", "success")
        return redirect(url_for('admin.added_background_image'))
    return render_template('admin/background/add_image.html', form=form)

# Background Image Delete Method 
@admin.route('/background_image/delete/<int:background_image_id>', methods=['POST', 'GET'])
@admin_required
def delete_background_image(background_image_id):
    background_image_data = BackgroundImage.query.get(background_image_id)
    db.session.delete(background_image_data)
    db.session.commit()
    flash("Image Deleted Successfully.", "success")
    return redirect(url_for('admin.added_background_image'))

@admin.route('/logo')
@login_required
@admin_required
def added_logo():
    """View available logo image"""
    data = Logo.query.first()
    if data is None:
        return redirect(url_for('admin.add_logo'))
    return render_template(
        'admin/logo/added_logo.html', data=data)

# Logo add method
@admin.route('/logo/add', methods=['POST', 'GET'])
@admin_required
def add_logo():
    form = WebsiteLogoForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['logo_image'])
        logo = Logo(logo_image=image)
        db.session.add(logo)
        db.session.commit()
        flash("Logo Added Successfully .", "success")
        return redirect(url_for('admin.added_logo'))
    return render_template('admin/logo/add_logo.html', form=form)

# Logo Delete Method 
@admin.route('/logo/delete/<int:logo_id>', methods=['POST', 'GET'])
@admin_required
def delete_logo(logo_id):
    logo_data = Logo.query.get(logo_id)
    db.session.delete(logo_data)
    db.session.commit()
    flash("Logo Deleted Successfully.", "success")
    return redirect(url_for('admin.add_logo'))

@admin.route('/brandname', methods=['GET', 'POST'])
@login_required
@admin_required
def add_brand_name():
    """Add a new brand name."""
    item = BrandName.query.first()
    if item is not None:
        return redirect(url_for('admin.added_brandname'))
        
    form = BrandNameForm()
    if form.validate_on_submit():
        data = BrandName(
            text=form.text.data
            )
        db.session.add(data)
        db.session.commit()
        flash('BrandName {} successfully created'.format(data.text),
              'form-success')
        return redirect(url_for('admin.added_brandname'))
    return render_template('admin/brandname/add_brandname.html', form=form)

@admin.route('/brandname-list')
@login_required
@admin_required
def added_brandname():
    """View added brand name."""
    data = BrandName.query.first()
    return render_template(
        'admin/brandname/added_brandname.html', data=data)

@admin.route('/brandname/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_brandname(id):
    """Delete the brand name """
    data = BrandName.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.brand_name'))

@admin.route('/seo-list')
@login_required
@admin_required
def added_seo():
    """View all added SEO texts."""
    data = Seo.query.first()
    if data is None:
        return redirect(url_for('admin.add_seo'))
    return render_template(
        'admin/seo/added_seo.html', data=data)

# Add SEO 
@admin.route('/seo/add', methods=['POST', 'GET'])
@admin_required
def add_seo():
    form = SeoForm()
    if form.validate_on_submit():
        data = Seo(
            title=form.title.data,
            content=form.content.data
            )
        db.session.add(data)
        db.session.commit()
        flash("SEO Added Successfully.", "success")
        return redirect(url_for('admin.added_seo'))
    return render_template('admin/seo/add_seo.html', form=form)

# Edit SEO 
@admin.route('/seo/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_seo(id):
    data = Seo.query.filter_by(id=id).first()
    form = SeoForm(obj=data)
    if form.validate_on_submit():
        data.title=form.title.data
        data.content=form.content.data
        db.session.add(data)
        db.session.commit()
        flash("SEO Added Successfully.", "success")
        return redirect(url_for('admin.added_seo'))
    else:
        flash('ERROR! SEO was not edited.', 'error')
    return render_template('admin/seo/add_seo.html', form=form)

@admin.route('/seo/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_seo(id):
    """Delete the seo texts """
    data = Seo.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    if data is None:
        return redirect(url_for('admin.add_seo'))
    return redirect(url_for('admin.added_seo'))


@admin.route('/footertext-list')
@login_required
@admin_required
def added_footertext():
    """View added footer text."""
    data = FooterText.query.first()
    if data is None:
        return redirect(url_for('admin.add_footertext'))
    return render_template(
        'admin/footertext/added_footertext.html', data=data)

# Add FooterText 
@admin.route('/footer/add', methods=['POST', 'GET'])
@admin_required
def add_footertext():
    form = FooterTextForm()
    if form.validate_on_submit():
        data = FooterText(
            title=form.title.data
            )
        db.session.add(data)
        db.session.commit()
        flash("Footer Text Added Successfully.", "success")
        return redirect(url_for('admin.added_footertext'))
    return render_template('admin/footertext/add_footertext.html', form=form)


# Edit SEO 
@admin.route('/footertext/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_footertext(id):
    data = FooterText.query.filter_by(id=id).first()
    form = FooterTextForm(obj=data)
    if form.validate_on_submit():
        data.title=form.title.data
        db.session.add(data)
        db.session.commit()
        flash("Edit successfully.", "success")
        return redirect(url_for('admin.added_footertext'))
    else:
        flash('ERROR! Text was not edited.', 'error')
    return render_template('admin/footertext/add_footertext.html', form=form)

@admin.route('/footer/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_footertext(id):
    """Delete the item """
    data = FooterText.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_footertext'))

@admin.route('/icon-list')
@login_required
@admin_required
def added_icons():
    """View all added icons."""
    data = SocialMediaIcon.query.all()
    if data is None:
        return redirect(url_for('admin.add_icon'))
    return render_template(
        'admin/icon/added_icon.html', data=data)

# Add Icon 
@admin.route('/icon/add', methods=['POST', 'GET'])
@admin_required
def add_icon():
    form = SocialMediaIconForm()
    if form.validate_on_submit():
        data = SocialMediaIcon(
            icon=form.icon.data,
            url_link=form.url_link.data
            )
        db.session.add(data)
        db.session.commit()
        flash("Icon Added Successfully.", "success")
        return redirect(url_for('admin.added_icons'))
    return render_template('admin/icon/add_icon.html', form=form)

# Edit Icon 
@admin.route('/icon/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_icon(id):
    data = SocialMediaIcon.query.filter_by(id=id).first()
    form = SocialMediaIconForm(obj=data)
    if form.validate_on_submit():
        data.icon=form.icon.data
        data.url_link=form.url_link.data
        db.session.add(data)
        db.session.commit()
        flash("Icon Added Successfully.", "success")
        return redirect(url_for('admin.added_icon'))
    else:
        flash('ERROR! icon was not edited.', 'error')
    return render_template('admin/icon/add_icon.html', form=form)

@admin.route('/icon/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_icon(id):
    """Delete the item """
    data = SocialMediaIcon.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_icon'))

@admin.route('/copyright-list')
@login_required
@admin_required
def added_copyright():
    """View added copyright text."""
    data = CopyRight.query.first()
    if data is None:
        return redirect(url_for('admin.add_copyright'))
    return render_template(
        'admin/copyright/added_copyright.html', data=data)

# Add CopyRight 
@admin.route('/copyright/add', methods=['POST', 'GET'])
@admin_required
def add_copyright():
    form = CopyRightForm()
    if form.validate_on_submit():
        data = CopyRight(
            text=form.text.data
            )
        db.session.add(data)
        db.session.commit()
        flash("CopyRight Text Added Successfully.", "success")
        return redirect(url_for('admin.added_copyright'))
    return render_template('admin/copyright/add_copyright.html', form=form)


# Edit Copyright
@admin.route('/copyright/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_copyright(id):
    data = CopyRight.query.filter_by(id=id).first()
    form = CopyRightForm(obj=data)
    if form.validate_on_submit():
        data.text=form.text.data
        db.session.add(data)
        db.session.commit()
        flash("Edit successfully.", "success")
        return redirect(url_for('admin.added_copyright'))
    else:
        flash('ERROR! Text was not edited.', 'error')
    return render_template('admin/copyright/add_copyright.html', form=form)

@admin.route('/copyright/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_copyright(id):
    """Delete the item """
    data = CopyRight.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_copyright'))

@admin.route('/favicon-image')
@login_required
@admin_required
def added_favicon_image():
    """View available favicon image"""
    data = FaviconImage.query.first()
    if data is None:
        return redirect(url_for('admin.add_favicon_image'))
    return render_template(
        'admin/favicon/added_images.html', data=data)

# Favicon Image add method
@admin.route('/favicon_image/add', methods=['POST', 'GET'])
@admin_required
def add_favicon_image():
    form = FaviconImageForm(request.form)
    if request.method == 'POST':
        image = images.save(request.files['favicon_image'])
        favicon_image = FaviconImage(favicon_image=image)
        db.session.add(favicon_image)
        db.session.commit()
        flash("Favicon Added Successfully .", "success")
        return redirect(url_for('admin.added_favicon_image'))
    return render_template('admin/favicon/add_image.html', form=form)

# Favicon Image Delete Method 
@admin.route('/favicon_image/delete/<int:favicon_image_id>', methods=['POST', 'GET'])
@admin_required
def delete_favicon_image(favicon_image_id):
    favicon_image_data = FaviconImage.query.get(favicon_image_id)
    db.session.delete(favicon_image_data)
    db.session.commit()
    flash("Image Deleted Successfully.", "success")
    return redirect(url_for('admin.added_favicon_image'))


@admin.route('/trackingscript-list')
@login_required
@admin_required
def added_trackingscript():
    """View added tracking script."""
    data = TrackingScript.query.all()
    if data is None:
        return redirect(url_for('admin.add_trackingscript'))
    return render_template(
        'admin/trackingscript/added_trackingscript.html', data=data)

# Add TrackingScript 
@admin.route('/trackingscript/add', methods=['POST', 'GET'])
@admin_required
def add_trackingscript():
    form = TrackingScriptForm()
    if form.validate_on_submit():
        data = TrackingScript(
            name=form.name.data,
            script=form.script.data
            )
        db.session.add(data)
        db.session.commit()
        flash("Tracking Script Added Successfully.", "success")
        return redirect(url_for('admin.added_trackingscript'))
    return render_template('admin/trackingscript/add_trackingscript.html', form=form)


# Edit SEO 
@admin.route('/trackingscript/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_trackingscript(id):
    data = TrackingScript.query.filter_by(id=id).first()
    form = TrackingScriptForm(obj=data)
    if form.validate_on_submit():
        data.name=form.name.data
        data.script=form.script.data
        db.session.add(data)
        db.session.commit()
        flash("Edit successfully.", "success")
        return redirect(url_for('admin.added_trackingscript'))
    else:
        flash('ERROR! Text was not edited.', 'error')
    return render_template('admin/trackingscript/add_trackingscript.html', form=form)

@admin.route('/trackingscript/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_trackingscript(id):
    """Delete the item """
    data = TrackingScript.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_trackingscript'))
