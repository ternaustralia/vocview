from pyldapi.renderer import Renderer
from pyldapi.view import View
from flask import render_template, Response
from rdflib import URIRef, Graph
from rdflib.namespace import SKOS


import skos
from skos.common_properties import CommonPropertiesMixin
from config import Config


class Collection(CommonPropertiesMixin):
    def __init__(self, uri):
        CommonPropertiesMixin.__init__(self, uri)
        super().__init__(uri)
        self.skos_members = skos.get_members(uri)
        # self.concept_hierarchy = skos.get_concept_hierarchy(uri) TODO: skos:member is enough.


class CollectionRenderer(Renderer):
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

        for s, p, o in Config.g.triples((URIRef(self.uri), None, None)):
            g.add((s, p, o))

        return Response(g.serialize(format=self.format), mimetype=self.format)

    def render(self):
        if self.view == 'skos':
            if self.format == 'text/html':
                cc = skos.Collection(self.uri)
                return render_template('skos.html', title=cc.label, c=cc,
                                       skos_class=('http://www.w3.org/2004/02/skos/core#ConceptScheme', 'Collection'),
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
            return super(Collection, self).render()