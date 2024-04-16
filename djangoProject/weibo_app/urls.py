from django.urls import path, include
from rest_framework import routers
from . import views

#将我们movieInfo这个模型相关的api注册到我们视图中
router = routers.DefaultRouter()
router.register(r'contentList', views.WeiboRawViewSet)

urlpatterns = [
    path('', include(router.urls)),
    #自定义的接口
    path('top10f',views.top10Fview),
    # path('movie_month_grow',views.movie_month_grow),
    # path('movie_type_calc',views.movie_type_calc),
    # path('movie_score_order',views.movie_score_order),
    # path('movie_area_calc', views.movie_area_calc),
]