from SPARQLWrapper import SPARQLWrapper, JSON

from config import Config

import pickle
import os


def _load_from_disk():
    # TODO: Check if cache is invalidated, and don't load if it is invalid.
    try:
        with open(os.path.join(Config.APP_DIR, 'sites.p'), 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(e)
        return None


def get():
    sites = _load_from_disk()

    if not sites:
        sites = []

        sparql = SPARQLWrapper('http://graphdb-dev.tern.org.au/repositories/CORVEG-1')
        sparql.setQuery("""
            PREFIX plot: <http://linked.data.gov.au/def/plot/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            select * where {
                ?site_uri a plot:Site .
                ?site_uri rdfs:label ?label .
                ?site_uri dct:description ?description .
            }
        """)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        for result in results['results']['bindings']:
            sites.append((
                result['site_uri']['value'],
                result['label']['value'],
                [('http://purl.org/dc/terms/description', result['description']['value'])]
            ))
            # sites.append({
            #         'site_uri': result['site_uri']['value'],
            #         'label': result['label']['value'],
            #         'description': result['description']['value']
            #     })

        with open(os.path.join(Config.APP_DIR, 'sites.p'), 'wb') as f:
            pickle.dump(sites, f)

    return sites
