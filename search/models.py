import re
from itertools import chain

from django.db import models
from django.core.exceptions import ValidationError
from model_utils.models import TimeStampedModel

class CampaignNameField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length']=32
        super(CampaignNameField, self).__init__(*args, **kwargs)
        self._re = re.compile(r"^\w{4,32}$")

    def clean(self, value, model_instance):
        value = super(models.CharField, self).clean(value, model_instance).strip()
        matched = self._re.match(value)
        if not matched:
            raise ValidationError("Name must be a word made of 4 to 32 characters.")
        setattr(model_instance, self.name, value)
        return value
    

class Campaign(TimeStampedModel):
    name = CampaignNameField(unique=True)

    @property
    def run_set(self):
        qs = Run.objects.none()
        for dork in self.dork_set.all():
            qs |= dork.run_set
        return qs

    @property
    def result_set(self):
        qs = Result.objects.none()
        for run in self.run_set.all():
            qs |= run.result_set.filter()
        return qs

# TODO: move somewhere else, create a testsuite and remove redundant tests from ./tests.py
class DorkQueryField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs['max_length']=256
        super(DorkQueryField, self).__init__(*args, **kwargs)
        self._re = re.compile(r"^.{1,256}$")

    def clean(self, value, model_instance):
        value = super(models.CharField, self).clean(value, model_instance).strip()
        matched = self._re.match(value)
        if not matched:
            raise ValidationError("Name must be a word made of 1 to 256 characters.")
        setattr(model_instance, self.name, value)
        return value

class Dork(TimeStampedModel):
    campaign = models.ForeignKey('Campaign')
    query = DorkQueryField()

    @property
    def result_set(self):
        qs = Dork.objects.none()
        for run in self.run_set.all():
            qs |= run.result_set
        return qs

    class Meta:
        unique_together = ("campaign", "query")

class Run(models.Model):
    dork = models.ForeignKey('Dork')
    result_set = models.ManyToManyField('Result')
    created = models.DateTimeField(auto_now_add=True)

class Result(models.Model):
    title = models.CharField(max_length=1024)
    summary = models.TextField()
    url = models.URLField(max_length=1024)

    class Meta:
        unique_together = ("title", "summary", "url")
