# from scoring.settings import APIKEY


def api_login(_function):
    pass
    # def wrap(request, *args, **kwargs):
    #     if APIKEY == request.POST.get('apikey') and len(APIKEY) > 15:
    #         return _function(request, *args, **kwargs)
    #     else:
    #         return RequestFailed()
    #
    # wrap.__doc__ = _function.__doc__
    # wrap.__name__ = _function.__name__
    # return wrap


def has_test_coverage(wrapped_function):
    def _wrapper(*args, **kwargs):
        result = wrapped_function(*args, **kwargs)
        return result

    return _wrapper
