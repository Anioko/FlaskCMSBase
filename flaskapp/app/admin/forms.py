from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    FloatField,
    MultipleFileField,
    FileField,
    SelectField,
    DateField, 
    TextAreaField,
    IntegerField,
    BooleanField

)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    DataRequired
)

from app import db
from app.models import Role, User, BlogCategory, BlogTag, BlogNewsLetter
from wtforms_alchemy import Unique, ModelForm, model_form_factory
from flask_uploads import UploadSet, IMAGES

images = UploadSet('images', IMAGES)

BaseModelForm = model_form_factory(FlaskForm)


class ChangeUserEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 64),
                                 Email()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangeAccountTypeForm(FlaskForm):
    role = QuerySelectField(
        'New account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    submit = SubmitField('Update role')


class InviteUserForm(FlaskForm):
    role = QuerySelectField(
        'Account type',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(Role).order_by('permissions'))
    first_name = StringField(
        'First name', validators=[InputRequired(),
                                  Length(1, 64)])
    last_name = StringField(
        'Last name', validators=[InputRequired(),
                                 Length(1, 64)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 64),
                             Email()])
    submit = SubmitField('Invite')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class NewUserForm(InviteUserForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])

    submit = SubmitField('Create')

class ModuleCrudForm(BaseModelForm):
    """Client Form ."""
    name = StringField("Name", validators=[DataRequired(), Length(min=5, max=80)])
    description = StringField("Description", validators=[DataRequired(), Length(min=5, max=256)])
    long_description = TextAreaField("Long Description", validators=[DataRequired(), Length(min=5)])
    tags = StringField("Tags (comma separated)", validators=[DataRequired(), Length(min=5)])
    demo_url = StringField("Demo Url", validators=[DataRequired(), Length(min=5, max=256)])
    code_path = StringField("Code Path", validators=[DataRequired(), Length(min=5, max=256)])
    price = FloatField("Price", validators=[DataRequired()])
    support_price = FloatField("Support Price", validators=[DataRequired()])
    release_date = DateField("Release Date", validators=[DataRequired()])
    last_update_date = DateField("Release Date", validators=[DataRequired()])
    image = FileField('Product Image (397x306)', validators=[FileRequired(), FileAllowed(images, 'Images only allowed!')])
    images = MultipleFileField('Product Screenshots (726x403)', validators=[DataRequired(), FileAllowed(images, 'Images only!')])


class SlideShowCrudForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=2, max=80)])
    image = FileField('SlideShow Image (928x413)', validators=[FileRequired(), FileAllowed(images, 'Images only allowed!')])
    submit = SubmitField('Submit')

class SeoForm(FlaskForm):
    #meta_tag = SelectField(u'Meta Tag',choices=[('name','name'),('property','property')] ,validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=80)])
    content = StringField("Meta Description, 180 words maximum", validators=[DataRequired(), Length(min=5, max=181)])
    submit = SubmitField('Submit')

#############################################################
class HomeTextForm(BaseModelForm):
    firstext = StringField("First Title", validators=[DataRequired(), Length(min=5, max=80)])
    secondtext = StringField("Second Title", validators=[DataRequired(), Length(min=25, max=80)])
    submit = SubmitField('Submit')

#############################################################
class NavMenuForm(FlaskForm):
    text = StringField("Text etc Contact", validators=[DataRequired(), Length(min=3, max=80)])
    url = StringField("Url e.g /account/login ", validators=[DataRequired(), Length(min=5, max=80)])
    submit = SubmitField('Submit')
    
class CallToActionForm(FlaskForm):
    text = StringField("Call to action text")
    url = StringField("Call to action url e.g /account/login ")
    submit = SubmitField('Submit')

class TechnologiesForm(FlaskForm):
    firstext = StringField("First Title", validators=[DataRequired(), Length(min=5, max=80)])
    secondtext = StringField("Second Title", validators=[DataRequired(), Length(min=10, max=80)])
    submit = SubmitField('Submit')

class TrackingScriptForm(FlaskForm):
    name = StringField("Script Name e.g Hotjar or Google Analytics", validators=[DataRequired(), Length(min=2, max=25)])
    script = TextAreaField("Paste the raw script")
    submit = SubmitField('Submit')
    
class ImageTechnologyForm(FlaskForm):
    image = FileField('Technology Image (128x128)', validators=[FileRequired(), FileAllowed(images, 'Images only allowed!')])
    submit = SubmitField('Submit')
    
class WebsiteLogoForm(BaseModelForm):
    logo_image = FileField('Logo Image (182x33). A transparent logo is better', validators=[FileRequired(), FileAllowed(images, 'Logo Only allowed!')])
    submit = SubmitField('Submit')
    
class BackgroundImageForm(FlaskForm):
    background_image = FileField('Background (1920x794)', validators=[FileRequired(), FileAllowed(images, 'Images Only allowed!')])
    submit = SubmitField('Submit')

class FaviconImageForm(FlaskForm):
    favicon_image = FileField('Background (32x32)', validators=[FileRequired(), FileAllowed(images, 'Images Only allowed!')])
    submit = SubmitField('Submit')
    
# Footer Text Form
class FooterTextForm(BaseModelForm):
    title = TextAreaField("Long Description", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Submit')


# Social Media Form 
class SocialMediaIconForm(FlaskForm):
    # image = FileField('Logo Image (128x128)', validators=[FileRequired(), FileAllowed(images, 'Social Iocn Image Only!')])
    icon = StringField("Icon Html Code(fab fa-facebook-f)", validators=[DataRequired()])
    url_link = StringField("Icon Link, e.g https://www.facebook.com/PastorChrisLive ", validators=[DataRequired()])
    submit = SubmitField('Submit')
    
# Brand Name Form Model
class BrandNameForm(FlaskForm):
    text = StringField("Brand Name E.g Nokia ", validators=[DataRequired(), Length(min=2, max=15)])
    submit = SubmitField('Submit')

# Copyright Form Model
class CopyRightForm(FlaskForm):
    text = StringField("Copyright Footer Text", validators=[DataRequired(), Length(min=6, max=60)])
    submit = SubmitField('Submit')

# Footer Image Model Form
class FooterImageForm(BaseModelForm):
    image = FileField('Footer Image', validators=[FileRequired(), FileAllowed(images, "Image Allowed Only !")])


# Resource Title Role Model Form
class ResourcesForm(BaseModelForm):
    role_title = StringField("Role Add ...", validators=[DataRequired(), Length(min=3, max=20)])


# Resource Detais Add with Role
class ResourceDetailAddForm(BaseModelForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=5, max=20)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(min=5)])
class BlogCategoryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    order = IntegerField('Order', validators=[InputRequired()])
    is_featured = BooleanField("Is Featured ?")
    submit = SubmitField('Submit')



#blog
class BlogTagForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    submit = SubmitField('Submit')


class BlogNewsLetterForm(BaseModelForm):
    email = EmailField('Email', validators=[InputRequired(), Length(1, 64), Email(), Unique(BlogNewsLetter.email)])
    submit = SubmitField('Submit')


class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    text = CKEditorField('Body', validators=[InputRequired()])
    image = FileField('Image', validators=[InputRequired(), FileAllowed(images, 'Images only!')])
    categories = QuerySelectMultipleField(
        'Categories',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(BlogCategory).order_by('order'))
    tags = QuerySelectMultipleField(
        'Tags',
        validators=[InputRequired()],
        get_label='name',
        query_factory=lambda: db.session.query(BlogTag).order_by('created_at'))
    newsletter = BooleanField('Send Announcement To Subscribers.')
    all_users = BooleanField('Send Announcement To All Users.')

    submit = SubmitField('Submit')
