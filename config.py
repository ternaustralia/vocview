import os


class Config:
    # Subdirectory of base URL. Example, the '/corveg' part of 'vocabs.tern.org.au/corveg'
    SUB_URL = ''

    # Path of the application's directory.
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    # Vocabulary sources config. file.
    VOCAB_SOURCES = 'vocabs.yaml'
