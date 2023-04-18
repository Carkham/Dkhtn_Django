import json


# POST请求格式解析
class PostParser:
    def __init__(self, body: bytes):
        self.obj = json.loads(body)

    def get(self, key: str):
        return self.obj[key]


class JsonReq:
    def __init__(self, body: bytes):
        self.POST = PostParser(body)
