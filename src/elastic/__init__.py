import elasticsearch


def get_client(host, port, timeout=300):
    port = int(port)
    scheme = 'https' if port == 443 else None
    auth = None

    if '@' in host:
        auth, host = host.split('@')
        username, password = auth.split(':')
        auth = (username, password)

    return elasticsearch.Elasticsearch([host], http_auth=auth, scheme=scheme, port=port)
