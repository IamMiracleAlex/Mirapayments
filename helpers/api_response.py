from collections import OrderedDict

from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer


class SuccessResponse():
    '''Standardise API Responses and add additional keys'''
    
    def __new__(cls,  detail = 'success', data={}, status=status.HTTP_200_OK):
        return Response(
            {
                'status': True,
                'detail': detail,
                'data': data
            },
            status
        )

class FailureResponse():
    def __new__(cls, detail = 'error', status=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                'status': False,
                'detail': detail
            },
            status
        )


class CustomJSONRenderer(JSONRenderer):
    '''Override the default JSON renderer to be consistent and have addition keys'''

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status = renderer_context['response'].status_code < 400
      
        if isinstance(data, dict):
            data = OrderedDict(data.items())
        data['status'] = status    
        if not data.__contains__('detail'):
            data['detail'] = 'success' if status else 'error'
        data.move_to_end('detail', last=False)
        data.move_to_end('status', last=False)
        return super(CustomJSONRenderer, self).render(data, accepted_media_type, renderer_context)