from flask import Flask, render_template
from flask.ext.assets import Bundle, Environment

app = Flask(__name__)
assets = Environment(app)

css = Bundle('css/bootstrap.css')
assets.register('css_all', css)

js = Bundle('js/bootstrap.js')
assets.register('js_all', js)


@app.route('/')
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/gallery/<slug>')
def detail(slug):
    return render_template('detail.html')


@app.route('/prices')
def prices():
    return render_template('prices.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
