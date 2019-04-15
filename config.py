import os


class Config:
    # Path of the application's directory.
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    # Vocabulary sources config. file.
    VOCAB_SOURCES = 'vocabs.yaml'
