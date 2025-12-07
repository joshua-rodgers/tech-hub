from flask import Flask, redirect, url_for
from techhub_blueprint import bp as techhub_bp, init_app

app = Flask(__name__)

# Register blueprint and configure app
app.register_blueprint(techhub_bp)
init_app(app)

@app.route('/')
def index():
    return redirect(url_for('techhub.index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
