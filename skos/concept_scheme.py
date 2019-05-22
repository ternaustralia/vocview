from pyldapi.renderer import Renderer
from pyldapi.view import View
from flask import render_template, Response
from rdflib import URIRef, Graph
from rdflib.namespace import SKOS


import skos
from skos.common_properties import CommonPropertiesMixin
from config import Config


class ConceptScheme(CommonPropertiesMixin):
    def __init__(self, uri):
        super().__init__(uri)
        self.concept_hierarchy = skos.get_concept_hierarchy(uri)


class ConceptSchemeRenderer(Renderer):
    def __init__(self, uri, request):
        self.uri = uri

        views = {
            'skos': View(
                'SKOS',
                'Simple Knowledge Organization System (SKOS) is an area of work developing specifications and standards to support the use of knowledge organization systems (KOS) such as thesauri, classification schemes, subject heading lists and taxonomies within the framework of the Semantic Web.',
                ['text/html'] + Renderer.RDF_MIMETYPES,
                'text/html',
                namespace='http://www.w3.org/2004/02/skos/core#'
            )
        }

        super().__init__(request, uri, views, 'skos')

    def _add_concept_by_narrower(self, g, concept):
        for narrower_concept in g.objects(concept, SKOS.narrower):
            for subj, pred, obj in Config.g.triples((narrower_concept, None, None)):
                g.add((subj, pred, obj))
                self._add_concept_by_narrower(g, narrower_concept)

    def _render_skos_rdf(self):
        # TODO: Add this inference algorithm to start-up so that each concept within a concept scheme is tagged with
        #       the property skos:InScheme. This will reduce the RDF load-time for concept schemes that have lots of
        #       narrower concepts.
        #       .
        #       This method should then be replaced with just getting the concept scheme and concept by skos:inScheme.
        g = Graph()

        # Get the concept scheme properties
        for subj, pred, obj in Config.g.triples((URIRef(self.uri), None, None)):
            g.add((subj, pred, obj))

        # Get the concepts by skos;inScheme
        for concept in Config.g.subjects(SKOS.inScheme, URIRef(self.uri)):
            for subj, pred, obj in Config.g.triples((concept, None, None)):
                g.add((subj, pred, obj))

        # Get the concepts by skos:topConceptOf
        for concept in Config.g.subjects(SKOS.topConceptOf, URIRef(self.uri)):
            self._add_concept_by_narrower(g, concept)

        return Response(g.serialize(format=self.format), mimetype=self.format)

    def render(self):
        if self.view == 'skos':
            if self.format == 'text/html':
                cc = skos.ConceptScheme(self.uri)
                return render_template('skos.html', title=cc.label, c=cc,
                                       skos_class=('http://www.w3.org/2004/02/skos/core#ConceptScheme', 'Concept Scheme'),
                                       formats=[(format, format.split('/')[-1]) for format in self.views.get('skos').formats])
            elif self.format in Renderer.RDF_MIMETYPES:
                return self._render_skos_rdf()
            else:
                # In theory, this line should never execute because if an invalid format has been entered, the pyldapi
                # will default to the default format. In this case, The default format for the default view (skos) is
                # text/html.
                raise RuntimeError('Invalid format error')
        else:
            # Let pyldapi handle the rendering of the 'alternates' view.
            return super(ConceptSchemeRenderer, self).render()
