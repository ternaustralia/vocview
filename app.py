from flask import Flask, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

import logging

from config import Config
from controller.routes import routes
import helper
from triplestore import Triplestore

logging.basicConfig(level=logging.INFO)

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
    logging.info('Loaded config:')
    logging.info(Config.__dict__)


@app.context_processor
def context_processor():
    return dict(h=helper, config=Config)


if __name__ == '__main__':
    # Run this only for development. Production version should use a dedicated WSGI server.
    if Config.SUB_URL:
        print('Starting simple server')
        run_simple('0.0.0.0', port=5000, application=application, use_reloader=True)
    else:
        print('Starting Flask server')
        app.run(host='0.0.0.0', port='5000', debug=True)