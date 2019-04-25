import os


class Config:
    # URL root of this web application. This gets set in the before_first_request function.
    url_root = None

    # Subdirectory of base URL. Example, the '/corveg' part of 'vocabs.tern.org.au/corveg'
    SUB_URL = ''

    # Path of the application's directory.
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    # Vocabulary sources config. file.
    VOCAB_SOURCES = 'vocabs.yaml'

    # Or provide a SPARQL endpoint
    sparql_endpoint = 'http://demo.ands.org.au/repository/api/sparql/tern-rva_tern-corveg-vocabularies_v0-212'

    # Rule-based reasoner
    reasoner = False

    # -- Triplestore ---------------------------------------------------------------------------------------------------
    #
    # Options:
    #
    # - memory
    #   - No persistence, load in triples on instance start-up (slow start-up time). Graph is required to be kept in
    #     memory during application's lifetime. Not recommended due to slow start-up.
    #   - Difficulty: easy
    #
    # - pickle
    #   - Persistent store by saving a binary (pickle) copy of the Python rdflib.Graph object to disk. Graph is
    #     required to be in memory during application's lifetime. Fast start-up time and fast performance, uses
    #     significantly more memory than Sleepycat. Exact same as the memory method except it persists between
    #     application restarts.
    #   - Difficulty: easy
    #
    # - sleepycat
    #   - Persistent store by storing the triples in the now defunct Sleepycat's Berkeley DB store. Requires external
    #     libraries to be installed on the system before using. Does not require to have the whole triplestore in
    #     memory. Performance is slightly slower than the pickle method (maybe around 10-20%) but uses much less memory.
    #     For each request, only the required triples are loaded into the application's memory.
    #   - Difficulty: intermediate
    triplestore_type = 'pickle'

    # Triplestore disk path
    _triplestore_name_pickle = 'triplestore.p'
    triplestore_path_pickle = os.path.join(APP_DIR, _triplestore_name_pickle)
    _triplestore_name_sleepy_cat = 'triplestore'
    triplestore_path_sleepy_cat = os.path.join(APP_DIR, _triplestore_name_sleepy_cat)
