import atexit
import logging

from flask import Flask, request
from flask_cors import CORS
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
from watchdog.observers import Observer

from config import Config
from controller.routes import routes
import helper
from graph_management import get_graph, VocviewFileSystemEventHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(routes)

application = DispatcherMiddleware(
    None, {
        Config.SUB_URL: app
    }
)


# Set up python-watchdog
path = 'data'
observer = Observer()
observer.schedule(VocviewFileSystemEventHandler(), path)
observer.start()


@app.before_request
def before():
    # Config.g = Triplestore.get_db(Config.triplestore_type)
    Config.g = get_graph(Config)


@app.after_request
def after(response):
    return response


@app.before_first_request
def init():
    # Set the URL root of this web application
    Config.url_root = request.url_root
    logging.info('Loaded config:')
    logging.info(Config.__dict__)

    logging.info('Triggering background task from vocview app.')
    import worker  # Import to create directories if missing.
    from tasks import fetch_data
    fetch_data.s().apply_async()


@app.context_processor
def context_processor():
    return dict(h=helper, config=Config)


@atexit.register
def shutdown():
    logger.info('Performing cleanup')
    observer.stop()


if __name__ == '__main__':
    # Run this only for development. Production version should use a dedicated WSGI server.
    if Config.SUB_URL:
        print('Starting simple server')
        run_simple('0.0.0.0', port=5000, application=application, use_reloader=True)
    else:
        print('Starting Flask server')
        app.run(host='0.0.0.0', port='5000', debug=True)
