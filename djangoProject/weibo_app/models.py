from django.db import models
import json
# Create your models here.

class WeiboRaw(models.Model):
    id = models.BigAutoField(primary_key=True)
    userid = models.CharField(max_length=20)
    username = models.CharField(max_length=45)
    user_gender = models.CharField(max_length=10)
    user_followers = models.CharField(max_length=45, default='0')
    post_time = models.CharField(max_length=45)
    thumbs_up = models.CharField(max_length=45, default='0')
    comments = models.CharField(max_length=45, default='0')
    reposts = models.CharField(max_length=45, default='0')
    content = models.TextField()

    #store as int
    comments_int = models.IntegerField(default=0)
    reposts_int = models.IntegerField(default=0)
    thumbs_up_int = models.IntegerField(default=0)
    user_followers_int = models.IntegerField(default=0)

    def toJSON(self):
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

    class Meta:
        app_label = 'weibo_app'
        db_table = 'weibo_raw1'
        verbose_name = 'Weibo Raw1'
        verbose_name_plural = 'Weibo Raws1'
        # ordering = ['id', 'userid', 'username', 'user_gender', 'user_followers', 'post_time', 'thumbs_up', 'reposts', 'comments', 'user_followers_int', 'thumbs_up_int', 'reposts_int', 'comments_int', 'content']


#粉丝数前10
class WeiboTop10F(models.Model):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=45)
    user_followers = models.CharField(max_length=45)

    class Meta:
        app_label = 'weibo_app'
        db_table = 'weibo_top10f'
        verbose_name = 'Weibo Top10Followers'
        verbose_name_plural = 'Weibo Top10Followers'

    # def save(self, *args, **kwargs):
    #     print(self.__dict__, 'saved')
    #     super().save(*args, **kwargs)