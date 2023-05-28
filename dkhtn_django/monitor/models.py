from django.db import models
from dkhtn_django.user.models import User


# Create your models here.

class Templates(models.Model):
    template_id = models.BigAutoField(primary_key=True)
    image_name = models.CharField(max_length=256)
    template_label = models.CharField(max_length=128)
    dockerfile = models.TextField(db_column='Dockerfile', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = True
        db_table = 'templates'


class SourceVersions(models.Model):
    version_id = models.BigAutoField(primary_key=True)
    version_label = models.CharField(max_length=128)
    content = models.TextField()
    requirements = models.TextField()
    source = models.ForeignKey('Sources', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'source_versions'
        unique_together = (('source', 'version_label'), ('source', 'version_label'),)


class Sources(models.Model):
    source_id = models.BigAutoField(primary_key=True)
    source_name = models.CharField(max_length=128)
    template = models.ForeignKey(to=Templates, to_field="template_id", on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, models.DO_NOTHING)
    image_name = models.CharField(max_length=128, blank=True, null=True)
    image_version = models.ForeignKey('SourceVersions', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sources'


class Functions(models.Model):
    function_id = models.BigAutoField(primary_key=True)
    function_label = models.CharField(max_length=128)
    source = models.ForeignKey(to=Sources, to_field="source_id", on_delete=models.DO_NOTHING)
    user = models.ForeignKey(to=User, to_field="id", on_delete=models.DO_NOTHING)
    trigger_id = models.BigIntegerField()
    running = models.IntegerField(blank=True, null=True)
    deployment_name = models.CharField(max_length=128, blank=True, null=True)
    running_version_id = models.BigIntegerField(blank=True, null=True)
    call_count = models.BigIntegerField(blank=True, null=True)
    error_count = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'functions'
        unique_together = (('user', 'function_label'),)
