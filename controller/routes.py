from flask import Blueprint, render_template, request
from munch import munchify
from pyldapi.register_renderer import RegisterRenderer
from pyldapi.view import View

import skos
from config import Config

routes = Blueprint('routes', __name__)


@routes.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@routes.route('/vocabulary/', methods=['GET'])
def render_vocabulary_register():
    concept_schemes = munchify(skos.list_concept_schemes())

    r = skos.Register(request, 'Register of SKOS vocabularies', 'This register contains a listing of SKOS vocabularies as concept schemes or collections.', concept_schemes, ['http://www.w3.org/2004/02/skos/core#ConceptScheme'], register_template='register.html', description='Register of all vocabularies in this system. Vocabularies are encoded using the SKOS model.')
    return r.render()

    # views = {
    #     'skos': View(
    #         'SKOS',
    #         'Simple Knowledge Organization System (SKOS) is an area of work developing specifications and standards to support the use of knowledge organization systems (KOS) such as thesauri, classification schemes, subject heading lists and taxonomies within the framework of the Semantic Web.',
    #         ['text/html'],
    #         'text/html',
    #         namespace='http://www.w3.org/2004/02/skos/core#'
    #     )
    # }
    # kwargs = { 'title': 'Home', 'length': len(Config.g), 'concept_schemes': concept_schemes }
    # r = RegisterRenderer(request, request.base_url, 'Register of SKOS vocabularies', 'This register contains a listing of SKOS vocabularies as concept schemes or collections.', concept_schemes, ['http://www.w3.org/2004/02/skos/core#ConceptScheme'], len(concept_schemes), register_template='index.html')
    # return r.render()

    # return render_template('index.html', title='Home', length=len(Config.g), concept_schemes=concept_schemes)


@routes.route('/vocabulary/<path:uri>', methods=['GET'])
def render_vocabulary_instance(uri):
    cc = skos.ConceptScheme(uri)
    return render_template('skos.html', title=cc.label, c=cc,
                           skos_class=('http://www.w3.org/2004/02/skos/core#ConceptScheme', 'Concept Scheme'))


@routes.route('/concept/', methods=['GET'])
def render_concept_register():
    concepts = munchify(skos.list_concepts())
    r = skos.Register(request, 'Register of SKOS concepts', 'This register contains a listing of all SKOS concepts within this system.', concepts, ['http://www.w3.org/2004/02/skos/core#Concept'], register_template='register.html', description='Register of all SKOS concepts in this system.')
    return r.render()


@routes.route('/concept/<path:uri>', methods=['GET'])
def render_concept(uri):
    c = skos.Concept(uri)
    return render_template('skos.html', title=c.label, c=c,
                           skos_class=('http://www.w3.org/2004/02/skos/core#Concept', 'Concept'))


@routes.route('/id/<path:uri>', methods=['GET'])
def ob(uri):
    skos_type = skos.get_uri_skos_type(uri)

    if skos_type == skos.CONCEPTSCHEME:
        cc = skos.ConceptScheme(uri)
        return render_template('skos.html', title=cc.label, c=cc, skos_class=('http://www.w3.org/2004/02/skos/core#ConceptScheme', 'Concept Scheme'))
    elif skos_type == skos.CONCEPT:
        c = skos.Concept(uri)
        return render_template('skos.html', title=c.label, c=c, skos_class=('http://www.w3.org/2004/02/skos/core#Concept', 'Concept'))

    return 'URI supplied does not exist or is not of type SKOS.'
