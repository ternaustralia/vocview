from rdflib import ConjunctiveGraph
from rdflib.store import NO_STORE, VALID_STORE
import yaml
from owlrl import DeductiveClosure, OWLRL_Semantics

from config import Config

import os
import pickle


class InvalidTriplestoreType(Exception):
    pass


class Triplestore:
    @staticmethod
    def get_db(triplestore_type):
        if triplestore_type == 'memory':
            g = Triplestore._create_db()
        elif triplestore_type == 'pickle':
            if os.path.isfile(Config.triplestore_path_pickle):
                with open(Config.triplestore_path_pickle, 'rb') as f:
                    g = pickle.load(f)
            else:
                g = Triplestore._create_db()
                with open(Config.triplestore_path_pickle, 'wb') as f:
                    pickle.dump(g, f)
        elif triplestore_type == 'sleepycat':
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
            for vocab in vocabs['download'].values():
                g.parse(vocab['source'], format=vocab['format'])

            # Local resources
            for vocab in vocabs['local'].values():
                g.parse(os.path.join(Config.APP_DIR, 'local_vocabs', vocab['source']), format=vocab['format'])

            # Expand graph using a rule-based inferencer.
            DeductiveClosure(OWLRL_Semantics).expand(g)
