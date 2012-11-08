import datetime
import logging
import os
import urlparse

from flask import Flask, flash, redirect, render_template, url_for
from flask.ext.assets import Bundle, Environment
from flask.ext.wtf import Email, Form, Required, TextAreaField, TextField as FormTextField
from flask.ext.wtf.html5 import EmailField
from flask_mail import Mail, Message
from flask_peewee.admin import Admin, ModelAdmin
from flask_peewee.auth import Auth
from flask_peewee.db import Database
from flask_peewee.utils import get_object_or_404
from peewee import BooleanField, CharField, DateTimeField, ForeignKeyField, TextField

logging.basicConfig(level=logging.INFO)

urlparse.uses_netloc.append('postgres')
url = urlparse.urlparse(os.environ['DATABASE_URL'])

DATABASE = {
    'engine': 'peewee.PostgresqlDatabase',
    'name': url.path[1:],
    'user': url.username,
    'password': url.password,
    'host': url.hostname,
    'port': url.port,
}

DEBUG = True
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = os.environ['SECRET_KEY']

MAIL_SERVER = 'smtp.mandrillapp.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ['MAIL_USERNAME']
MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
DEFAULT_MAIL_SENDER = ADMIN_EMAIL

app = Flask(__name__)
app.config.from_object(__name__)
assets = Environment(app)
db = Database(app)
auth = Auth(app, db)
admin = Admin(app, auth)
mail = Mail(app)

css = Bundle('css/bootstrap.css')
assets.register('css_all', css)

js = Bundle('js/bootstrap.js')
assets.register('js_all', js)


class Piece(db.Model):
    title = CharField()
    slug = CharField()
    url = CharField()
    created = DateTimeField(default=datetime.datetime.now)
    is_published = BooleanField(default=True)
    notes = TextField(null=True)

    def __unicode__(self):
        return '%s' % self.title


class PieceAdmin(ModelAdmin):
    columns = ('title', 'created', 'is_published',)


class PieceImage(db.Model):
    piece = ForeignKeyField(Piece, related_name='images')
    title = CharField()
    url = CharField()

    def __unicode__(self):
        return '%s' % self.title


class PieceImageAdmin(ModelAdmin):
    columns = ('title', 'piece', 'url',)

admin.register(Piece, PieceAdmin)
admin.register(PieceImage, PieceImageAdmin)
admin.setup()


class ContactForm(Form):
    name = FormTextField('Name', validators=[Required()])
    email = EmailField('Email', validators=[Required(), Email()])
    message = TextAreaField('Message', validators=[Required()])


@app.route('/')
@app.route('/gallery')
def gallery():
    pieces = Piece.select().where(Piece.is_published == True).order_by(Piece.created.desc())
    return render_template('gallery.html', pieces=pieces)


@app.route('/gallery/<slug>')
def detail(slug):
    piece = get_object_or_404(Piece.select().where(Piece.slug == slug))
    images = PieceImage.select().where(PieceImage.piece == piece)
    return render_template('detail.html', piece=piece, images=images)


@app.route('/prices')
def prices():
    return render_template('prices.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        msg = Message("Contact Form Submission (%s)" % email,
            reply_to=email,
            recipients=[ADMIN_EMAIL],
            body=message)
        mail.send(msg)

        logging.info('%s (%s): %s' % (name, email, message,))

        flash("Thanks for contacting me.. I'll get back to you as soon as possible!", 'success')
        return redirect(url_for('gallery'))
    return render_template('contact.html', form=form)

if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    Piece.create_table(fail_silently=True)
    PieceImage.create_table(fail_silently=True)

    app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
