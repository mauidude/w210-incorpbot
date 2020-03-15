import re

from elasticsearch import Elasticsearch, RequestsHttpConnection


def get_client(host, port, timeout=300, username=None, password=None):
    port = int(port)
    scheme = 'https' if port == 443 else 'http'
    auth = None

    if re.match(r'^https?://', host):
        index = host.index('://')
        scheme = host[0:index]
        host = host[index+3:]

    if '@' in host and username is None and password is None:
        auth, host = host.split('@')
        username, password = auth.split(':')
        auth = (username, password)
    elif username is not None or password is not None:
        auth = (username, password)

    return Elasticsearch([host], http_auth=auth, scheme=scheme, port=port, verify_certs=False, connection_class=RequestsHttpConnection)
