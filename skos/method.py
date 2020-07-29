from pyldapi.renderer import Renderer
from pyldapi.view import View
from flask import render_template, Response
from rdflib import Graph, URIRef, BNode

import skos
from skos.common_properties import CommonPropertiesMixin
from config import Config


class Method(CommonPropertiesMixin):
    def __init__(self, uri):
        CommonPropertiesMixin.__init__(self, uri)
        self.uri = uri
        self.purpose = skos.get_method_purpose(uri)
        self.scope = skos.get_method_scope(uri)
        self.equipment = skos.get_method_equipment(uri)
        self.instructions = skos.get_method_instructions(uri)


class MethodRenderer(Renderer):
    def __init__(self, uri, request):
        self.uri = uri

        views = {
            'method': View(
                'Method',
                'A TERN method.',
                ['text/html'] + Renderer.RDF_MIMETYPES,
                'text/html',
                namespace='https://w3id.org/tern/ontologies/skos/'
            )
        }

        super().__init__(request, uri, views, 'method')

    # TODO: Make a base class and make this a method of the base class.
    def render_rdf(self):
        g = Graph()

        for subj, pred, obj in Config.g.triples((URIRef(self.uri), None, None)):
            g.add((subj, pred, obj))
            if type(obj) == BNode:
                for s, p, o in Config.g.triples((obj, None, None)):
                    g.add((s, p, o))

        return Response(g.serialize(format=self.format), mimetype=self.format)

    def render(self):
        if not hasattr(self, 'format'):
            self.format = 'text/html'
        if self.view == 'method':
            if self.format == 'text/html':
                cc = Method(self.uri)
                return render_template('method.html', title=cc.label, c=cc,
                                       skos_class=('https://w3id.org/tern/ontologies/ssn/Method', 'Method'),
                                       formats=[(format, format.split('/')[-1]) for format in self.views.get('method').formats])
            elif self.format in Renderer.RDF_MIMETYPES:
                return self.render_rdf()
            else:
                # In theory, this line should never execute because if an invalid format has been entered, the pyldapi
                # will default to the default format. In this case, The default format for the default view (skos) is
                # text/html.
                raise RuntimeError('Invalid format error')
        else:
            # Let pyldapi handle the rendering of the 'alternates' view.
            return super(MethodRenderer, self).render()
