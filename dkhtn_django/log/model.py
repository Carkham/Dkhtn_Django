from django.db import models


class LogMessage(models.Model):
    id = models.AutoField
    timestamp = models.DateTimeField()
    function_id = models.CharField(max_length=255)
    level = models.CharField(max_length=255)
    message = models.TextField()
