import os

from rdflib import Graph
from owlrl import DeductiveClosure, OWLRL_Semantics
import yaml
from celery import Celery
from celery.utils.log import get_task_logger
from tern_rdf.utils import create_session

from config import Config

logger = get_task_logger(__name__)

app = Celery(__name__)

broker_url = os.getenv('CELERY_BROKER_URL', 'filesystem://')
broker_dir = os.getenv('CELERY_BROKER_FOLDER', './broker')


@app.on_after_configure.connect
def setup_period_tasks(sender, **kwargs):
    sender.add_periodic_task(float(Config.store_seconds), fetch_data.s(), name='Fetch data')


@app.task
def fetch_data():
    with open(os.path.join(Config.APP_DIR, Config.VOCAB_SOURCES)) as f:
        vocabs = yaml.safe_load(f)
        g = Graph()
        http = create_session()
        if vocabs.get('download'):
            for vocab in vocabs['download'].values():
                logger.info(f'Fetching from remote URL {vocab["source"]}')
                r = http.get(vocab['source'])
                r.raise_for_status()
                data = r.text
                g.parse(data=data, format=vocab['format'])
                logger.info(f'Success with code {r.status_code}')

        if Config.reasoner:
            DeductiveClosure(OWLRL_Semantics).expand(g)

        path = 'data/data.ttl'
        logger.info(f'Serializing to disk at path {path}')
        g.serialize(path, format='turtle')


app.conf.update({
    'broker_url': broker_url,
    'broker_transport_options': {
        'data_folder_in': os.path.join(broker_dir, 'out'),
        'data_folder_out': os.path.join(broker_dir, 'out'),
        'data_folder_processed': os.path.join(broker_dir, 'processed')
    },
    'imports': ('tasks',),
    'result_persistent': False,
    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json']})
