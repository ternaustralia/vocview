from flask import Flask, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from config import Config
from controller.routes import routes
import helper
from triplestore import Triplestore

app = Flask(__name__)
app.register_blueprint(routes)

application = DispatcherMiddleware(
    None, {
        Config.SUB_URL: app
    }
)


@app.before_request
def before():
    Config.g = Triplestore.get_db(Config.triplestore_type)


@app.after_request
def after(response):
    return response


@app.before_first_request
def init():
    # Set the URL root of this web application
    Config.url_root = request.url_root


@app.context_processor
def context_processor():
    return dict(h=helper, config=Config)


if __name__ == '__main__':
    run_simple('0.0.0.0', port=5000, application=application)