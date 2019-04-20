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

    # -- Triplestore ---------------------------------------------------------------------------------------------------
    #
    # Options:
    #
    # - memory
    #   - No persistence, load in triples on instance start-up. Graph is required to be kept in memory during
    #     application's lifetime.
    #   - Difficulty: basic
    #
    # - pickle
    #   - Persistent store by saving a binary (pickle) copy of the Python rdflib.Graph object to disk. Graph is
    #     required to be in memory during application's lifetime.
    #   - Difficulty: basic
    #
    # - sleepcat
    #   - Persistence through storing the data in the now defunct Sleepycat's Berkeley DB store. Requires external
    #     libraries to be installed on the system before using. Does not require to have
    #   - Difficulty: intermediate
    triplestore_type = 'pickle'

    # Triplestore disk path
    _triplestore_name_pickle = 'triplestore.p'
    triplestore_path_pickle = os.path.join(APP_DIR, _triplestore_name_pickle)
    _triplestore_name_sleepy_cat = 'triplestore'
    triplestore_path_sleepy_cat = os.path.join(APP_DIR, _triplestore_name_sleepy_cat)
