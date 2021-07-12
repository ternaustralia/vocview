import logging
import os
import time
import traceback
from typing import Type

from rdflib import Graph
from watchdog.events import FileSystemEventHandler

from config import Config

last_trigger_time = time.time()
logger = logging.getLogger(__name__)


def load_graph(set_on_config: bool = False):
    g = Graph()
    path = 'data/data.ttl'
    logger.info(f'Loading data from path {path}')
    if os.path.isfile(path):
        try:
            g.parse(path, format='turtle')
            logger.info(f'Loading completed.')
        except Exception:
            traceback.print_exc()
            # This block is only possible if load_graph() is triggered by watchdog.
            return None
    if set_on_config:
        Config.g = g
    return g


def get_graph(config: Type[Config]):
    if not hasattr(config, 'g'):
        return load_graph()
    else:
        return config.g


class VocviewFileSystemEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global last_trigger_time
        current_time = time.time()
        if event.src_path.find('~') == -1 and (current_time - last_trigger_time) > 1:
            last_trigger_time = current_time
            load_graph(set_on_config=True)
