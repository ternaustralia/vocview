# from rdflib import ConjunctiveGraph, Graph, URIRef, Literal
# from rdflib.namespace import DCTERMS, XSD
# import yaml
# from owlrl import DeductiveClosure, OWLRL_Semantics
# import requests
#
# from config import Config
#
# import os
# from datetime import datetime, timedelta
# import logging
# import time
#
#
# class InvalidTriplestoreType(Exception):
#     pass
#
#
# class Triplestore:
#     THIS_GRAPH = URIRef('http://www.this-graph.com/123456789/')
#     loading = False
#
#     @staticmethod
#     def get_db(triplestore_type):
#         if triplestore_type == 'memory':
#             if not hasattr(Config, 'g'):
#                 # g = Triplestore._create_db()
#                 g = Graph()
#             else:
#                 g = Config.g
#                 # for date in g.objects(Triplestore.THIS_GRAPH, DCTERMS.created):
#                 #     now = datetime.now()
#                 #     now -= timedelta(hours=Config.store_hours, minutes=Config.store_minutes)
#                 #     if now > date.toPython():
#                 #         g = Triplestore._create_db(g)
#         else:
#             raise InvalidTriplestoreType(
#                 'Expected one of: [memory]. Instead got {}'.format(triplestore_type))
#         return g
#
#     @staticmethod
#     def _create_db(old_g: Graph = None):
#         start_time = time.time()
#
#         g = ConjunctiveGraph()
#
#         if not Triplestore.loading:
#             logging.info('Creating new graph')
#             Triplestore.loading = True
#             Triplestore._add_triples(g)
#
#             # Add time of creation of new Graph
#             g.add((Triplestore.THIS_GRAPH, DCTERMS.created, Literal(datetime.now(), datatype=XSD.dateTime)))
#
#             logging.info(f'time taken: {(time.time() - start_time):.2f} seconds')
#             Triplestore.loading = False
#         else:
#             if old_g:
#                 return old_g
#
#         return g
#
#     @staticmethod
#     def _add_triples(g):
#         # Read in RDF from online sources to the Graph.
#         logging.info('Pulling RDF triples from remote resources.')
#         with open(os.path.join(Config.APP_DIR, Config.VOCAB_SOURCES)) as f:
#             vocabs = yaml.safe_load(f)
#
#             # Online resources
#             if vocabs.get('download'):
#                 for vocab in vocabs['download'].values():
#                     r = requests.get(vocab['source'])
#                     data = r.content.decode('utf-8')
#                     g.parse(format=vocab['format'], data=data)
#
#             # Local resources
#             if vocabs.get('local'):
#                 for vocab in vocabs['local'].values():
#                     g: Graph
#                     g.parse(os.path.join(Config.APP_DIR, 'local_vocabs', vocab['source']), format=vocab['format'])
#
#             # SPARQL resources
#             pass
#
#             # RVA
#             resource_endpoint = vocabs['rva']['resource_endpoint']
#             download_endpoint = vocabs['rva']['download_endpoint']
#             extension = vocabs['rva']['extension']
#             format = vocabs['rva']['format']
#             for id in vocabs['rva']['ids']:
#                 r = requests.get(resource_endpoint.format(id), headers={'accept': 'application/json'})
#                 try:
#                     response = r.json()
#                     versions = response['version']
#                     download_id = None
#                     for version in versions:
#                         if version['status'] == 'current':
#                             access_points = version['access-point']
#                             for access_point in access_points:
#                                 if access_point.get('ap-sesame-download'):
#                                     download_id = access_point['id']
#
#                             if download_id is None:
#                                 # Sesame endpoing not found, go for the Turtle file
#                                 for access_point in access_points:
#                                     if access_point.get('ap-file'):
#                                         g.parse(access_point['ap-file']['url'], format='turtle')
#
#                     if download_id:
#                         r = requests.get(download_endpoint.format(download_id), params={'format': extension})
#                         g.parse(data=r.content.decode('utf-8'), format=format)
#                 except Exception as e:
#                     raise Exception('Something wrong with the response of RVA ID {}. Error: {}'.format(id, e))
#
#             # Expand graph using a rule-based inferencer.
#             if Config.reasoner:
#                 DeductiveClosure(OWLRL_Semantics).expand(g)
