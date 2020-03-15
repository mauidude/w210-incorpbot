import elasticsearch


def get_client(host, port, timeout=300, username=None, password=None):
    port = int(port)
    scheme = 'https' if port == 443 else 'http'
    auth = None

    if '@' in host and username is None and password is None:
        auth, host = host.split('@')
        username, password = auth.split(':')
        auth = (username, password)
    elif username is not None or password is not None:
        auth = (username, password)

    return elasticsearch.Elasticsearch([host], http_auth=auth, scheme=scheme, port=port)
