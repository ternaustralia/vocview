from flask import Blueprint, render_template, request
from munch import munchify

import skos

routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@routes.route('/vocabulary/', methods=['GET'])
def render_vocabulary_register():
    concept_schemes = munchify(skos.list_concept_schemes())

    r = skos.Register(request, 'Register of SKOS vocabularies',
                      'This register contains a listing of SKOS vocabularies as concept schemes or collections.',
                      concept_schemes, ['http://www.w3.org/2004/02/skos/core#ConceptScheme'],
                      register_template='register.html',
                      description='Register of all vocabularies in this system. Vocabularies are encoded using the SKOS model.')
    return r.render()


@routes.route('/concept/', methods=['GET'])
def render_concept_register():
    concepts = munchify(skos.list_concepts())
    r = skos.Register(request,
                      'Register of SKOS concepts',
                      'This register contains a listing of all SKOS concepts within this system.',
                      concepts, ['http://www.w3.org/2004/02/skos/core#Concept'],
                      register_template='register.html',
                      description='Register of all SKOS concepts in this system.')
    return r.render()


@routes.route('/id/<path:uri>', methods=['GET'])
def ob(uri):
    skos_type = skos.get_uri_skos_type(uri)

    if skos_type == skos.CONCEPTSCHEME:
        r = skos.ConceptSchemeRenderer(uri, request)
        return r.render()
    elif skos_type == skos.CONCEPT:
        r = skos.ConceptRenderer(uri, request)
        return r.render()

    return 'URI supplied does not exist or is not a SKOS class.'
