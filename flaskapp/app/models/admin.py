import os

from flask import url_for

from app.database import Column, reference_col, relationship
from .. import db, login_manager
#from app.extensions import db, ma

############## = DateTime = ###########################
import datetime as dt
#######################################################
from flask_marshmallow import Marshmallow
#from marshmallow import Schema, fields

ma = Marshmallow()

class Module(db.Model):
    """A role for a user."""

    __tablename__ = "modules"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    demo_url = db.Column(db.String(256), nullable=False)
    code_path = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    support_price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(256), nullable=False)
    tags = db.Column(db.Text, nullable=False)
    # release_date = db.Column(db.Date, server_default='current_timestamp', default=db.func.now(), nullable=False)
    # last_update_date = db.Column(db.Date, server_default='current_timestamp', default=db.func.now(), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_update_date = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.image_filename, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image_filename)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class ModuleImage(db.Model):
    __tablename__ = "module_images"
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(256), nullable=False)

    #module_id = reference_col("modules", nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    module = relationship("Module", backref="screenshots")

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.image_filename, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image_filename)


class SlideShowImage(db.Model):
    __tablename__ = "slide_show_images"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    image_filename = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images',filename=self.image_filename, external=True)


    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image_filename)


class Seo(db.Model):
    __tablename__ = "seo"
    id = db.Column(db.Integer, primary_key=True)
    meta_tag = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(256), nullable=False)


class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(512), nullable=True)

#####################################################
#Front End chage models 

class HomeText(db.Model):
    __tablename__ = "hometext"
    id = db.Column(db.Integer, primary_key=True)
    firstext = db.Column(db.String(80), nullable=False)
    secondtext = db.Column(db.String(80), nullable=False)

class TrackingScript(db.Model):
    __tablename__ = "tracking_script"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    script = db.Column(db.String(150), nullable=False)

class TechnologiesText(db.Model):
    __tablename__ = "technologies_text"
    id = db.Column(db.Integer, primary_key=True)
    firstext = db.Column(db.String(80), nullable=False)
    secondtext = db.Column(db.String(80), nullable=False)


class CallToAction(db.Model):
    __tablename__ = "call_to_action"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(80), nullable=False)

class NavMenu(db.Model):
    __tablename__ = "nav_menu"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(80), nullable=False)

class TechnologiesImage(db.Model):
    __tablename__ = "technologies_images"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images',filename=self.image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image)


class Logo(db.Model):
    _tablename_ = "logo"
    id = db.Column(db.Integer, primary_key=True)
    logo_image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.logo_image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.logo_image)

class BackgroundImage(db.Model):
    _tablename_ = "background_image"
    id = db.Column(db.Integer, primary_key=True)
    background_image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.background_image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.background_image)


# Favicon Image Model 
class FaviconImage(db.Model):
    __tablename__ = "favicon_image"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image)
    

# Footer Image Model 
class FooterImage(db.Model):
    __tablename__ = "footerimage"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for('_uploads.uploaded_file', setname='images', filename=self.image, external=True)

    @property
    def image_path(self):
        from flask import current_app
        return os.path.join(current_app.config['UPLOADED_IMAGES_DEST'], self.image)


#Footer Text Model
class FooterText(db.Model):
    __tablename__ = "footertext"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)


# Footer Social Media Icon with link Model
class SocialMediaIcon(db.Model):
    __tablename__ = "socialmediaicon"
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(50), nullable=False)
    url_link = db.Column(db.String(256), nullable=False)


# Copyright text here
class BrandName(db.Model):
    __tablename__ = "brandname"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(15), nullable=False)

# Copyright text here
class CopyRight(db.Model):
    __tablename__ = "copyright"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(256), nullable=False)


# Resources List 
class Resource(db.Model):
    __tablename__ = "resource"
    id = db.Column(db.Integer, primary_key=True)
    role_title = db.Column(db.String(100), nullable=False)
    resourcedetails = db.relationship('ResourceDetail', backref='resource', uselist=False)


# Resources Details Models
class ResourceDetail(db.Model):
    __tablename__ = "resource_detail"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey('resource.id'))


# Schemas
class ModuleSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description", "price", "support_price", "image_url")
        module = Module
