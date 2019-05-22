from pyldapi.renderer import Renderer
from pyldapi.view import View
from flask import render_template, Response
from rdflib import Graph, URIRef

import skos
from skos.common_properties import CommonPropertiesMixin
from skos.schema_org import SchemaOrgMixin, SchemaPersonMixin
from config import Config


class Concept(CommonPropertiesMixin, SchemaOrgMixin, SchemaPersonMixin):
    def __init__(self, uri):
        CommonPropertiesMixin.__init__(self, uri)
        SchemaOrgMixin.__init__(self, uri)
        SchemaPersonMixin.__init__(self, uri)
        self.narrowers = skos.get_narrowers(uri)
        self.broaders = skos.get_broaders(uri)
        self.top_concept_of = skos.get_top_concept_of(uri)
        self.in_scheme = skos.get_in_scheme(uri)
        self.close_match = skos.get_close_match(uri)
        self.exact_match = skos.get_exact_match(uri)


class ConceptRenderer(Renderer):
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

    def _render_skos_rdf(self):
        g = Graph()

        for subj, pred, obj in Config.g.triples((URIRef(self.uri), None, None)):
            g.add((subj, pred, obj))

        return Response(g.serialize(format=self.format), mimetype=self.format)

    def render(self):
        if self.view == 'skos':
            if self.format == 'text/html':
                cc = skos.Concept(self.uri)
                return render_template('skos.html', title=cc.label, c=cc,
                                       skos_class=('http://www.w3.org/2004/02/skos/core#Concept', 'Concept'),
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
            return super(ConceptRenderer, self).render()
