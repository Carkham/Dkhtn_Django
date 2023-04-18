import json


class GetParser:
    """
    GET请求格式解析
    """
    def __init__(self, request):
        self.request = request

    def get(self, key):
        return self.request.GET.get(key)


class PostParser:
    """
    POST请求格式解析
    """
    def __init__(self, body: bytes):
        self.obj = json.loads(body)

    def get(self, key: str):
        return self.obj[key]


class JsonReq:
    """
    request请求格式解析
    """
    def __init__(self, request):
        if request.method == 'POST':
            self.POST = PostParser(request.body)
        elif request.method == 'GET':
            self.GET = GetParser(request)
