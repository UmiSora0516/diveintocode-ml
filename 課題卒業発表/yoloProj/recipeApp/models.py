from django.db import  models
from django.utils import timezone

class favorite(models.Model):
    registed_date = models.DateTimeField(default=timezone.now())
    recipe_id = models.CharField(max_length=100)
    recipe_title = models.CharField(max_length=1000)
    recipe_img_src = models.URLField()

