from django.db import models


class Selected(models.Model):
    user = models.OneToOneField("users.User", on_delete=models.CASCADE)
