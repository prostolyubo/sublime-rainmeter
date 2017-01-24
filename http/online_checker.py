import http.client


def __is_online(domain, sub_path, response_status, response_reason):
    conn = http.client.HTTPSConnection(domain, timeout=1)
    conn.request("HEAD", sub_path)
    response = conn.getresponse()
    conn.close()

    return (response.status == response_status) and (response.reason == response_reason)


def is_rm_doc_online():
    return __is_online("docs.rainmeter.net", "/manual-beta/", 200, "OK")


def is_gh_online():
    return __is_online("github.com", "/", 200, "OK")


def is_gh_raw_online():
    """
    Check if the raw content delivery from Github is online.

    It is routed to 301 and Moved Permanently because per standard it is routed to github.com
    because it natively only accepts real content paths.

    We do not follow reroutes else it would be 200 OK on github.com but we already have another method to check for that
    and Github.com is on a different service than the content delivery.
    """
    return __is_online("raw.githubusercontent.com", "/", 301, "Moved Permanently")
