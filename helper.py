from markdown import markdown
from flask import url_for
from rdflib.namespace import DCTERMS
from bs4 import BeautifulSoup

from config import Config
from triplestore import Triplestore

import re
from urllib.parse import quote_plus
from datetime import datetime, timedelta


def render_concept_tree(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')

    concept_hierarchy = soup.find(id='concept-hierarchy')

    uls = concept_hierarchy.find_all('ul')

    for i, ul in enumerate(uls):
        # Don't add HTML class nested to the first 'ul' found.
        if not i == 0:
            ul['class'] = 'nested'
            if ul.parent.name == 'li':
                temp = BeautifulSoup(str(ul.parent.a.extract()), 'html.parser')
                ul.parent.insert(0, BeautifulSoup('<span class="caret">', 'html.parser'))
                ul.parent.span.insert(0, temp)
    return soup


def get_triplestore_created_time():
    """Get the string message of the last time the local graph cache was created."""

    MSG = 'Last updated {}.'
    for created_time in Config.g.objects(Triplestore.THIS_GRAPH, DCTERMS.created):
        created_time = created_time.toPython()
        now = datetime.now()
        now -= timedelta(minutes=1)

        last_updated = (datetime.now() - created_time).seconds // 60
        if not last_updated:
            LAST_UPDATE_VALUE = 'just now'
        else:
            LAST_UPDATE_VALUE = f'{last_updated} minutes ago'

        return MSG.format(LAST_UPDATE_VALUE)


def uri_label(uri):
    return uri.split('#')[-1].split('/')[-1]


def render_property_restricted(text):
    if isinstance(text, str):
        length = 175
        if len(text) > length:
            return text[:length] + '...'
    return text


def is_list(property):
    if isinstance(property, list):
        return True
    return False


def render(text):
    if text[:4] == 'http':
        return '<p><a href="{0}">{0}</a></p>'.format(text)

    email_pattern = r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*" \
                    r"[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    if re.match(email_pattern, text):
        return '<p><a href="mailto:{0}">{0}</a></p>'.format(text)

    return markdown(text)


def url_encode(url):
    return quote_plus(url)


def render_instance_uri(uri, label):
    return '<a href="{}">{}</a>'.format(url_for('routes.ob', uri=uri), label)
