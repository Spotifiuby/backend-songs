class BlobMock:
    c = ""

    def upload_from_string(self, c):
        self.c = c
        return

    def download_as_string(self):
        return self.c


class BucketMock:
    d = dict()

    def blob(self, s):
        if s in self.d:
            return self.d[s]
        b = BlobMock()
        self.d[s] = b
        return b
