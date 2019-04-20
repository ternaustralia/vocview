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
                      title='Vocabularies',
                      description='Register of all vocabularies in this system.')
    return r.render()


@routes.route('/concept/', methods=['GET'])
def render_concept_register():
    concepts = munchify(skos.list_concepts())
    r = skos.Register(request,
                      'Register of SKOS concepts',
                      'This register contains a listing of all SKOS concepts within this system.',
                      concepts, ['http://www.w3.org/2004/02/skos/core#Concept'],
                      register_template='register.html',
                      title='Concepts',
                      description='Register of all vocabulary concepts in this system.')
    return r.render()


@routes.route('/id/<path:uri>', methods=['GET'])
def ob(uri):
    # TODO: Issue with Apache, Flask, and WSGI interaction where multiple slashes are dropped to 1 (19/04/2019).
    #       E.g. The URI http://linked.data.gov.au/cv/corveg/cover-methods when received at this endpoint becomes
    #       http:/linked.data.gov.au/cv/corveg/cover-methods. Missing slash after the HTTP protocol. This only happens
    #       using the Flask URL variable. It worked fine with query string arguments.
    #       .
    #       Reference issue online which describes the exact same issue here:
    #       - http://librelist.com/browser/flask/2012/8/24/not-able-to-pass-a-url-parameter-with-in-it/

    # Ugly fix for Apache multiple slash issue.

    # Get the protocol (http/https)
    protocol = uri.split(':')[0]

    # Fix the URI if it is missing double slash after the HTTP protocol.
    if protocol == 'http':
        if uri[6] != '/':
            uri = 'http://' + uri[6:]
    elif protocol == 'https':
        if uri[7] != '/':
            uri = 'https://' + uri[7:]

    skos_type = skos.get_uri_skos_type(uri)

    if skos_type == skos.CONCEPTSCHEME:
        r = skos.ConceptSchemeRenderer(uri, request)
        return r.render()
    elif skos_type == skos.CONCEPT:
        r = skos.ConceptRenderer(uri, request)
        return r.render()

    return 'URI supplied does not exist or is not a SKOS class.'
