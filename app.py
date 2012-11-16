import datetime
import logging
import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask.ext.assets import Bundle, Environment
from flask.ext.wtf import Email, Form, Required, TextAreaField, TextField as FormTextField
from flask.ext.wtf.html5 import EmailField
from flask_mail import Mail, Message
from flask_peewee.admin import Admin, ModelAdmin
from flask_peewee.auth import Auth
from flask_peewee.db import Database
from flask_peewee.utils import get_object_or_404
from peewee import BooleanField, CharField, DateTimeField, ForeignKeyField, TextField
import stripe

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.config.from_object(os.environ['CONFIG'])
assets = Environment(app)
db = Database(app)
auth = Auth(app, db)
admin = Admin(app, auth)
mail = Mail(app)

css = Bundle('css/bootstrap.css', 'css/custom.css')
assets.register('css_all', css)

js = Bundle('js/bootstrap.js')
assets.register('js_all', js)

stripe.api_key = app.config['STRIPE_KEYS']['secret_key']


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
    return render_template(
        'detail.html',
        piece=piece,
        images=images,
        available_sizes=app.config['AVAILABLE_SIZES'],
        stripe_key=app.config['STRIPE_KEYS']['publishable_key']
    )


@app.route('/charge', methods=['POST'])
def charge():
    size_id = request.form['size']
    size = filter(lambda size: size['id'] == size_id, app.config['AVAILABLE_SIZES'])[0]
    piece = Piece.get(Piece.id == request.form['piece'])

    # Amount in cents
    amount = size['price']
    description = '%s (%sx%s)' % (piece.title, size['width'], size['height'])

    stripe_response = stripe.Charge.create(
        amount=amount,
        currency='cad',
        card=request.form['stripeToken'],
        description=description
    )

    logging.info('ITEM PURCHASE: %s - %s' % (request.form, stripe_response,))

    flash("Thank you so much for purchasing this piece. I know you'll love it! Email mwarkentin@gmail.com or call 647-880-0174 if you have any questions.", 'success')
    return redirect(url_for('detail', slug=piece.slug))


@app.route('/prices')
def prices():
    return render_template(
        'prices.html',
        available_sizes=app.config['AVAILABLE_SIZES']
    )


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data

        msg = Message("Contact Form Submission (%s)" % email,
            reply_to=email,
            recipients=[app.config['ADMIN_EMAIL']],
            body=message)
        mail.send(msg)

        logging.info('%s (%s): %s' % (name, email, message,))

        flash("Thanks for contacting me.. I'll get back to you as soon as possible!", 'success')
        return redirect(url_for('gallery'))
    return render_template('contact.html', form=form)


auth.User.create_table(fail_silently=True)
Piece.create_table(fail_silently=True)
PieceImage.create_table(fail_silently=True)

admin.register(Piece, PieceAdmin)
admin.register(PieceImage, PieceImageAdmin)
admin.setup()
