from django.shortcuts import render

# Create your views here.
from django.db.models import IntegerField
from django.db.models.functions import Cast
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from .models import WeiboRaw, WeiboTop10F
from .serializers import WeiboRawSerializer, WeiboTop10FSerializer
from django.http import HttpResponse


class WeiboRawViewSet(viewsets.ModelViewSet):
    """
    允许用户查看或编辑的API路径。
    """
    queryset = WeiboRaw.objects.all()
    serializer_class = WeiboRawSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def top10Fview(request):
    """
    列出所有的code snippet，或创建一个新的snippet。
    """
    snippets = WeiboTop10F.objects.all()
    serializer = WeiboTop10FSerializer(snippets, many=True)
    return JSONResponse(serializer.data)