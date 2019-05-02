from rdflib import ConjunctiveGraph, Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, XSD
from rdflib.store import NO_STORE, VALID_STORE
import yaml
from owlrl import DeductiveClosure, OWLRL_Semantics
import requests

from config import Config

import os
import pickle
from datetime import datetime, timedelta


class InvalidTriplestoreType(Exception):
    pass


class Triplestore:
    THIS_GRAPH = URIRef('http://www.this-graph.com/123456789/')

    @staticmethod
    def _create_pickle_disk():
        print('creating new pickle disk')
        g = Triplestore._create_db()

        # Add time of creation of new Graph
        g.add((Triplestore.THIS_GRAPH, DCTERMS.created, Literal(datetime.now(), datatype=XSD.dateTime)))

        with open(Config.triplestore_path_pickle, 'wb') as f:
            pickle.dump(g, f)
        return g

    @staticmethod
    def get_db(triplestore_type):
        if triplestore_type == 'memory':
            g = Triplestore._create_db()
        elif triplestore_type == 'pickle':
            # Load pickled Graph object from disk. Check the time. If time has passed specified duration, then
            # re-harvest data.
            if os.path.isfile(Config.triplestore_path_pickle):
                with open(Config.triplestore_path_pickle, 'rb') as f:
                    g = pickle.load(f)
                    for date in g.objects(Triplestore.THIS_GRAPH, DCTERMS.created):
                        now = datetime.now()
                        now -= timedelta(hours=Config.store_hours, minutes=Config.store_minutes)
                        if now > date.toPython():
                            g = Triplestore._create_pickle_disk()
            else:
                g = Triplestore._create_pickle_disk()
        elif triplestore_type == 'sleepycat':
            # TODO: Re-harvest like 'pickle'.
            if hasattr(Config, 'g'):
                # Config has a Graph object, reuse it and open the persistent store.
                g = Config.g
                rt = g.open(Config.triplestore_path_sleepy_cat, create=False)
            else:
                # If this is the initial load and Config does not have a Graph object in memory, then create it.
                g = ConjunctiveGraph('Sleepycat')
                rt = g.open(Config.triplestore_path_sleepy_cat, create=False)

            if rt == NO_STORE:
                g.open(Config.triplestore_path_sleepy_cat, create=True)
                Triplestore._add_triples(g)
            else:
                assert rt == VALID_STORE, 'The underlying store is corrupt'
        # elif triplestore_type == 'sparql':
        #     if os.path.isfile(Config.triplestore_path_pickle):
        #         with open(Config.triplestore_path_pickle, 'rb') as f:
        #             g = pickle.load(f)
        #     else:
        #         sparql = SPARQLWrapper(Config.sparql_endpoint)
        #         sparql.setQuery("""DESCRIBE * WHERE {
        #             ?s ?p ?o .
        #         }""")
        #         sparql.setReturnFormat(N3)
        #         results = sparql.query().convert()
        #         g = Graph().parse(data=results, format='n3')
        #         with open(Config.triplestore_path_pickle, 'wb') as f:
        #             pickle.dump(g, f)
        else:
            raise InvalidTriplestoreType(
                'Expected one of: [memory, pickle, sleepycat]. Instead got {}'.format(triplestore_type))
        return g

    @staticmethod
    def _create_db():
        g = ConjunctiveGraph()

        Triplestore._add_triples(g)

        return g

    @staticmethod
    def _add_triples(g):
        # Read in RDF from online sources to the Graph.
        with open(os.path.join(Config.APP_DIR, Config.VOCAB_SOURCES)) as f:
            vocabs = yaml.safe_load(f)

            # Online resources
            if vocabs.get('download'):
                for vocab in vocabs['download'].values():
                    g.parse(vocab['source'], format=vocab['format'])

            # Local resources
            if vocabs.get('local'):
                for vocab in vocabs['local'].values():
                    g.parse(os.path.join(Config.APP_DIR, 'local_vocabs', vocab['source']), format=vocab['format'])

            # SPARQL resources
            pass

            # RVA
            resource_endpoint = vocabs['rva']['resource_endpoint']
            download_endpoint = vocabs['rva']['download_endpoint']
            extension = vocabs['rva']['extension']
            format = vocabs['rva']['format']
            for id in vocabs['rva']['ids']:
                r = requests.get(resource_endpoint.format(id), headers={'accept': 'application/json'})
                try:
                    response = r.json()
                    versions = response['version']
                    download_id = None
                    for version in versions:
                        if version['status'] == 'current':
                            access_points = version['access-point']
                            for access_point in access_points:
                                if access_point.get('ap-sesame-download'):
                                    download_id = access_point['id']
                    if download_id:
                        r = requests.get(download_endpoint.format(download_id), params={'format': extension})
                        g.parse(data=r.content.decode('utf-8'), format=format)
                except Exception as e:
                    raise Exception('Something wrong with the response of RVA ID {}. Error: {}'.format(id, e))


            # Expand graph using a rule-based inferencer.
            if Config.reasoner:
                DeductiveClosure(OWLRL_Semantics).expand(g)
