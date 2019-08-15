from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from rdflib import Graph, URIRef
from tern_rdf import TernRdf, RDFS, PLOTX, DCTERMS, SSN_EXT, LOCN, GEOSPARQL, W3CGEO, PLOT
from flask import render_template, Response
from pyldapi import Renderer, View

from config import Config
import skos

import pickle
import os
from datetime import date
import datetime


SPARQL_ENDPOINT = 'http://graphdb-dev.tern.org.au/repositories/CORVEG-1'


def _load_from_disk():
    """
    Load plot:Site register data from disk.

    :return:
    """
    try:
        cache_path = os.path.join(Config.APP_DIR, 'sites.p')
        t = os.path.getmtime(cache_path)
        cache_time = datetime.datetime.fromtimestamp(t)
        print(cache_time)

        today = datetime.datetime.now()
        new_time = datetime.datetime(today.year, today.month, today.day - 1)

        # Check if the cache is longer than a day old. If it is, return None.
        if not new_time > cache_time:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        print(e)
        return None


def get_all():
    """
    Retrieve a list of all CORVEG plot:Sites from disk/triple-store for register use.

    :return:
    """
    sites = _load_from_disk()

    if not sites:
        sites = []

        sparql = SPARQLWrapper(SPARQL_ENDPOINT)
        sparql.setQuery("""
            PREFIX plot: <http://linked.data.gov.au/def/plot/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            select * where {
                ?site_uri a plot:Site .
                ?site_uri rdfs:label ?label .
                optional {?site_uri dct:description ?description .}
            }
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            d = result.get('description')
            if d is not None:
                d = d.get('value')
            description = [('http://purl.org/dc/terms/description', d)]
            sites.append((
                result['site_uri']['value'],
                result['label']['value'],
                description if description is not None else None
            ))

        with open(os.path.join(Config.APP_DIR, 'sites.p'), 'wb') as f:
            pickle.dump(sites, f)

    return sites


def _get_site_label(uri: str, g: Graph):
    for label in g.objects(URIRef(uri), RDFS.label):
        return label


def _get_site_modified(uri: str, g: Graph):
    for modified in g.objects(URIRef(uri), DCTERMS.modified):
        modified = modified.split('-')
        modified = date(int(modified[0]), int(modified[1]), int(modified[2][:2]))
        return modified


def _get_site_description(uri: str, g: Graph):
    for desc in g.objects(URIRef(uri), DCTERMS.description):
        return desc


def _get_site_number(uri: str, g: Graph):
    q = f"""
    PREFIX dct: <http://purl.org/dc/terms/>
    select ?site_no 
    where {{
        <{uri}> dct:identifier ?site_no .
        filter((datatype(?site_no) = <http://linked.data.gov.au/def/corveg/site-number>))
    }}
    """
    result = g.query(q)
    site_no = None
    for row in result:
        site_no = row['site_no']
    return site_no


def _get_site_id(uri: str, g: Graph):
    q = f"""
        PREFIX dct: <http://purl.org/dc/terms/>
        select ?site_id 
        where {{
            <{uri}> dct:identifier ?site_id .
            filter((datatype(?site_id) = <http://linked.data.gov.au/def/corveg/site-id>))
        }}
        """
    result = g.query(q)
    site_id = None
    for row in result:
        site_id = row['site_id']
    return site_id


def _get_site_bioregion(uri: str, g: Graph):
    for bioregion in g.objects(URIRef(uri), SSN_EXT.hasUltimateFeatureOfInterest):
        label = skos.get_label(bioregion)
        return (bioregion, label)


def _get_site_floristics(uri: str, g: Graph):
    for floristics in g.objects(URIRef(uri), PLOTX.floristics):
        label = skos.get_label(floristics)
        return (floristics, label)


def _get_site_sample_type(uri: str, g: Graph):
    for sample_type in g.objects(URIRef(uri), PLOTX.sampleType):
        label = skos.get_label(sample_type)
        return (sample_type, label)


def _get_site_sample_level(uri: str, g: Graph):
    for sample_type in g.objects(URIRef(uri), PLOTX.sampleLevel):
        label = skos.get_label(sample_type)
        return (sample_type, label)


def _get_site_location_uri(uri: str, g: Graph):
    for location in g.objects(URIRef(uri), LOCN.location):
        return location


def _get_site_location_id(uri: str, g: Graph):
    for id in g.objects(URIRef(uri), DCTERMS.identifier):
        return id


def _get_location_object(uri: str, g: Graph):
    for location in g.objects(URIRef(uri), GEOSPARQL.hasGeometry):
        return location


def _get_site_location_lat(uri: str, g: Graph):
    location = _get_location_object(uri, g)
    if location is not None:
        for lat in g.objects(location, W3CGEO.lat):
            return lat


def _get_site_location_long(uri: str, g: Graph):
    location = _get_location_object(uri, g)
    if location is not None:
        for long in g.objects(location, W3CGEO.long):
            return long


def _get_site_location_label(uri: str, g: Graph):
    for label in g.objects(URIRef(uri), RDFS.label):
        return label


def _get_site_location_method(uri: str, g: Graph):
    for method in g.objects(URIRef(uri), PLOT.locationMethod):
        label = skos.get_label(method)
        return (method, label)


def _get_site_location_mapsheet_name(uri: str, g: Graph):
    for name in g.objects(URIRef(uri), PLOT.mapsheetName):
        return name


def _get_site_location_mapsheet_number(uri: str, g: Graph):
    for number in g.objects(URIRef(uri), PLOT.mapsheetNumber):
        return number


def _get_site_location_mapscale(uri: str, g: Graph):
    for scale in g.objects(URIRef(uri), PLOT.mapScale):
        label = skos.get_label(scale)
        return (scale, label)


def _get_site_location_name(uri: str, g: Graph):
    for name in g.objects(URIRef(uri), LOCN.geographicName):
        return name


class Site:
    def __init__(self, uri, g):
        self.uri = uri
        self.label = _get_site_label(uri, g)

        self.modified = _get_site_modified(uri, g)
        self.description = _get_site_description(uri, g)
        self.site_number = _get_site_number(uri, g)
        self.site_id = _get_site_id(uri, g)
        self.bioregion = _get_site_bioregion(uri, g)

        self.floristics = _get_site_floristics(uri, g)
        self.sample_type = _get_site_sample_type(uri, g)
        self.sample_level = _get_site_sample_level(uri, g)

        # Location
        self.location_uri = _get_site_location_uri(uri, g)
        self.location_label = _get_site_location_label(self.location_uri, g)
        self.location_modified = _get_site_modified(self.location_uri, g)
        self.location_id = _get_site_location_id(self.location_uri, g)
        self.location_geographic_name = _get_site_location_name(self.location_uri, g)
        self.location_description = _get_site_description(self.location_uri, g)
        self.lat = _get_site_location_lat(self.location_uri, g)
        self.long = _get_site_location_long(self.location_uri, g)
        self.location_method = _get_site_location_method(self.location_uri, g)
        self.mapsheet_name = _get_site_location_mapsheet_name(self.location_uri, g)
        self.mapsheet_number = _get_site_location_mapsheet_number(self.location_uri, g)
        self.map_scale = _get_site_location_mapscale(self.location_uri, g)


class SiteRenderer(Renderer):
    def __init__(self, uri, request, g: Graph):
        self.uri = uri
        self.g = g

        views = {
            'plot': View(
                'Plot',
                'Plot Ontology',
                ['text/html'] + Renderer.RDF_MIMETYPES,
                'text/html',
                namespace='http://linked.data.gov.au/def/plot/'
            )
        }

        super().__init__(request, uri, views, 'plot')

    def _render_plot_rdf(self):
        return Response(self.g.serialize(format=self.format), mimetype=self.format)

    def render(self):
        if self.view == 'plot':
            if self.format == 'text/html':
                s = Site(self.uri, self.g)
                return render_template('site.html', title=s.label, s=s, formats=[(format, format.split('/')[-1]) for format in self.views.get('plot').formats])
            elif self.format in Renderer.RDF_MIMETYPES:
                return self._render_plot_rdf()
            else:
                raise RuntimeError('Invalid format error. Pyldapi did not set to default.')
        else:
            return super(SiteRenderer, self).render()


def get(uri: str, request, rdf_format):
    """
    Get a plot:Site by its URI.

    :param uri: plot:Site URI.
    :return:
    """

    sparql = SPARQLWrapper(SPARQL_ENDPOINT)
    sparql.setQuery(f"""
        PREFIX plot: <http://linked.data.gov.au/def/plot/>
        PREFIX locn: <http://www.w3.org/ns/locn#>
        describe <{uri}> ?location where {{
            <{uri}> a plot:Site .
            <{uri}> locn:location ?location .
        }}
    """)

    sparql.setReturnFormat(TURTLE)
    results = sparql.query().convert()

    # print(results.decode('utf-8'))

    g = TernRdf.Graph().parse(data=results, format='turtle')

    g.update("""
        DELETE WHERE {
            ?thing <http://www.w3.org/ns/sosa/hasFeatureOfInterest> ?site .
        }
    """)

    if not len(g):
        return None

    s_renderer = SiteRenderer(uri, request, g)
    if rdf_format:
        s_renderer.format = rdf_format
    return s_renderer.render()
