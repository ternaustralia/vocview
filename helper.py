import re
from markdown import markdown


def uri_label(uri):
    return uri.split('#')[-1].split('/')[-1]


def render(text):
    if text[:4] == 'http':
        return '<p><a href="{0}">{0}</a></p>'.format(text)

    email_pattern = r"[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*" \
                    r"[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    if re.match(email_pattern, text):
        return '<p><a href="mailto:{0}">{0}</a></p>'.format(text)

    return markdown(text)
