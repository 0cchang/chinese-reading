from django.db import models

class CharMap(models.Model):
    chinese = models.CharField(max_length=1, default="_")
    english = models.CharField(max_length=50, default="empty")
    c_id = models.IntegerField(default = -999)

    def __str__(self):
        return self.chinese