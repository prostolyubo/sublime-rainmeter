"""
This module handles every related to online checking.

We need to request several information from various providers.
We could just try to request them, but instead
you can ping them first and check if they are even reachable.
This does not mean, that do not need to handle a failure on their part
(e.g. if the server is responding, but can't deliver the information).
"""


from http.client import HTTPSConnection


def _is_online(domain, sub_path, response_status, response_reason):
    conn = HTTPSConnection(domain, timeout=1)
    conn.request("HEAD", sub_path)
    response = conn.getresponse()
    conn.close()

    return (response.status == response_status) and (response.reason == response_reason)


def is_rm_doc_online():
    """
    Check if the Rainmeter documentation page is online.

    The Rainmeter online documentation is required to synchronize the local model
    with the latest online version. These information are stored and parsed
    to display them as a tooltip on special constructs.
    """
    return _is_online("docs.rainmeter.net", "/manual-beta/", 200, "OK")


def is_gh_online():
    """
    Check if GitHub is online.

    The different services of GitHub are running in seperat services
    and thus just being GitHub online does not mean,
    that required parts are online.
    """
    return _is_online("github.com", "/", 200, "OK")


def is_gh_raw_online():
    """
    Check if the raw content delivery from Github is online.

    It is routed to 301 and Moved Permanently because per standard it is routed to github.com
    because it natively only accepts real content paths.

    We do not follow reroutes else it would be 200 OK on github.com but we already have another method to check for that
    and Github.com is on a different service than the content delivery.
    """
    return _is_online("raw.githubusercontent.com", "/", 301, "Moved Permanently")
