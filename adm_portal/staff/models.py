from django.db import models


class Flags(models.Model):
    key = models.CharField(blank=False, null=False, max_length=25, editable=False)
    value = models.CharField(blank=False, null=False, max_length=50, editable=False)

    created_by = models.CharField(blank=False, null=False, max_length=200, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "created_at"
