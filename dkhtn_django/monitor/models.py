from django.db import models


# Create your models here.

class Resource(models.Model):
    function_id = models.CharField(max_length=255, primary_key=True)
    state = models.PositiveSmallIntegerField()
    running_time = models.TimeField()
    call_times = models.IntegerField()
    error_times = models.IntegerField()
    cost = models.IntegerField()
