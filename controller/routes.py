from flask import Blueprint, render_template, request
from munch import munchify

import skos
from config import Config

routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET'])
def index():
    concept_schemes = munchify(skos.list_concept_schemes())
    return render_template('index.html', title='Home', length=len(Config.g), concept_schemes=concept_schemes)


@routes.route('/object', methods=['GET'])
def ob():
    uri = request.args.get('uri')

    skos_type = skos.get_uri_skos_type(uri)

    if skos_type == skos.CONCEPTSCHEME:
        cc = skos.ConceptScheme(uri)
        return render_template('concept-scheme.html', title=cc.label, c=cc, skos_class='SKOS Concept Scheme')
    elif skos_type == skos.CONCEPT:
        c = skos.Concept(uri)
        return render_template('concept-scheme.html', title=c.label, c=c, skos_class='SKOS Concept')

    return 'URI supplied does not exist or is not of type SKOS.'
