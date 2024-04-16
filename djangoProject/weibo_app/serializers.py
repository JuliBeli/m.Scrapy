from rest_framework import serializers
from .models import WeiboRaw
from .models import WeiboTop10F

class WeiboRawSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeiboRaw
        #所有内容
        fields = ['userid','username','user_gender', 'user_followers', 'post_time', 'thumbs_up',
                  'comments', 'reposts', 'content']

class WeiboTop10FSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeiboTop10F
        #前10的粉丝数和内容
        fields = ['id','username','user_followers']