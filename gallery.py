import datetime
import os

from flask import Flask, render_template
from flask.ext.assets import Bundle, Environment
from flask_peewee.admin import Admin, ModelAdmin
from flask_peewee.auth import Auth
from flask_peewee.db import Database
from flask_peewee.utils import get_object_or_404
from peewee import BooleanField, CharField, DateTimeField, ForeignKeyField, TextField


DATABASE = {
    'name': 'gallery.db',
    'engine': 'peewee.SqliteDatabase',
}
DEBUG = True
SECRET_KEY = os.environ['SECRET_KEY']

app = Flask(__name__)
app.config.from_object(__name__)
assets = Environment(app)
db = Database(app)
auth = Auth(app, db)
admin = Admin(app, auth)

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


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    auth.User.create_table(fail_silently=True)
    Piece.create_table(fail_silently=True)
    PieceImage.create_table(fail_silently=True)

    app.run(debug=True)
