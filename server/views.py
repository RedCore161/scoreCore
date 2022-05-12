from rest_framework.response import Response


class RequestSuccess(Response):
    def __init__(self, data=None, **kwargs):
        if data is None:
            data = {}
        data['success'] = True
        super().__init__(data=data, status=200, **kwargs)


class RequestFailed(Response):
    def __init__(self, data=None, **kwargs):
        if data is None:
            data = {}
        data['success'] = False
        super().__init__(data=data, status=400, **kwargs)
