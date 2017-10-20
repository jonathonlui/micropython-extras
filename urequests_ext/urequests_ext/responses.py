

class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            self._cached = self.raw.read()
            self.raw.close()
            self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


class RedirectResponse(Response):
    def __init__(self, f, raw_location_header):
        super().__init__(f)
        self.raw_location_header = raw_location_header
        self._cached_location = None

    @property
    def location(self):
        if not self._cached_location:
            _, location = self.raw_location_header.split(b':', 1)
            self._cached_location = location.strip()
            self.raw_location_header = None
        return self._cached_location


class ResponseWithHeaders(Response):
    def __init__(self, f, raw_header_list):
        super().__init__(f)
        self.raw_header_list = raw_header_list
        self._cached_headers = None

    def close(self):
        super().close()
        self.raw_header_list = None
        self._cached_headers = None

    @property
    def headers(self):
        if self._cached_headers is None:
            self._cached_headers = {}
            for l in self.raw_header_list:
                k, v = l.split(b':', 1)
                self._cached_headers[k.strip().lower()] = v.strip()
            self.raw_header_list = None
        return self._cached_headers
