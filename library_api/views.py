from django.utils.http import urlencode
from rest_framework.reverse import reverse


def reverse_with_params(*args, **kwargs):
    params = kwargs.pop("params", {})
    url = reverse(*args, **kwargs)
    if params:
        url += "?" + urlencode(params)
    return url
