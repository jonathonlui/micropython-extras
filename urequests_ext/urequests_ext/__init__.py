import usocket

capture_response_headers = False


def request(method, url, data=None, json=None, headers={}, stream=None):
    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][-1]
    s = usocket.socket()
    s.connect(addr)
    if proto == "https:":
        s = ussl.wrap_socket(s, server_hostname=host)
    s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
    if not "Host" in headers:
        s.write(b"Host: %s\r\n" % host)
    # Iterate over keys to avoid tuple alloc
    for k in headers:
        s.write(k)
        s.write(b": ")
        s.write(headers[k])
        s.write(b"\r\n")
    if json is not None:
        assert data is None
        import ujson
        data = ujson.dumps(json)
    if data:
        s.write(b"Content-Length: %d\r\n" % len(data))
    s.write(b"\r\n")
    if data:
        s.write(data)

    l = s.readline()
    protover, status, msg = l.split(None, 2)
    status = int(status)
    #print(protover, status, msg)
    if capture_response_headers:
        raw_response_headers = []
    while True:
        l = s.readline()
        if not l or l == b"\r\n":
            break
        #print(l)
        if l.startswith(b"Transfer-Encoding:"):
            if b"chunked" in l:
                raise ValueError("Unsupported " + l)
        elif l.startswith(b"Location:") and 300 <= status <= 399:
            from .responses import RedirectResponse
            resp = RedirectResponse(s, l)
            resp.status_code = status
            resp.reason = msg.rstrip()
            return resp

        if capture_response_headers:
            raw_response_headers.append(l)

    if capture_response_headers:
        from .responses import ResponseWithHeaders
        resp = ResponseWithHeaders(s, raw_response_headers)
    else:
        from .responses import Response
        resp = Response(s)
    resp.status_code = status
    resp.reason = msg.rstrip()
    return resp


def head(url, **kw):
    return request("HEAD", url, **kw)

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)
