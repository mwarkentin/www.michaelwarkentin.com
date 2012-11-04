from flask import Flask
app = Flask(__name__)


@app.route('/gallery')
def index():
    return 'Gallery page'


@app.route('/gallery/<slug>')
def detail(slug):
    return 'Detail page: %s' % slug


@app.route('/pricing')
def pricing():
    return 'Pricing page'


@app.route('/contact')
def contact():
    return 'Contact page'

if __name__ == '__main__':
    app.run()
