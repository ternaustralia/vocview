from markdown import markdown
from flask import url_for

from config import Config

import re
from urllib.parse import quote_plus


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
