from flask import Flask
import yaml
from rdflib import Graph
from owlrl import DeductiveClosure, OWLRL_Semantics

from config import Config
from controller.routes import routes
import helper

import os

app = Flask(__name__)
app.register_blueprint(routes)


@app.before_first_request
def init():
    # Create an RDFLib Graph and store it in Config class. Assume it is persistent until application server restarts.
    Config.g = Graph()

    # Read in RDF from online sources to the Graph.
    with open(os.path.join(Config.APP_DIR, Config.VOCAB_SOURCES)) as f:
        vocabs = yaml.safe_load(f)

        # Online resources
        for vocab in vocabs['download'].values():
            Config.g.parse(vocab['source'], format=vocab['format'])

        # Local resources
        for vocab in vocabs['local'].values():
            Config.g.parse(os.path.join(Config.APP_DIR, 'local_vocabs', vocab['source']), format=vocab['format'])

    # Expand graph using a rule-based inferencer.
    DeductiveClosure(OWLRL_Semantics).expand(Config.g)


@app.context_processor
def context_processor():
    return dict(h=helper)


if __name__ == '__main__':
    app.run(debug=True)
