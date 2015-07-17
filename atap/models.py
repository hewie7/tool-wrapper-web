 # -*- coding: utf8 -*-
from django.db import models
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Tool(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    program = models.CharField(max_length=500)
    mem = models.IntegerField(max_length=10, default=2000)
    cpu = models.CharField(max_length=250, default="require.CPU_SINGLE")
    io = models.BooleanField(default=False)
    disk_space = models.IntegerField(default=100)
    description = models.TextField(blank=True)
    author = models.ForeignKey(User)
    version = models.CharField(max_length=100, blank=True, help_text="版本", default="0.0.1")
    create_time = models.DateTimeField(default=datetime.datetime.now())
    modify_time = models.DateTimeField(default=datetime.datetime.now())
    state = models.CharField(max_length=250, default="pending")
    code = models.TextField(blank=True, default="")
    deleted = models.BooleanField(default=False)
    base = models.IntegerField(blank=True, default=-1)

    def __unicode__(self):
        return self.name


class ToolFiles(models.Model):
    id = models.AutoField(primary_key=True)
    tool = models.ForeignKey(Tool)
    attachment = models.FileField(upload_to="upload", blank=True, null=True)

# class Versions(models.Model):
#     id = models.AutoField(primary_key=True)
#     base = models.ForeignKey(Tool)
#     drive = models.ForeignKey(Tool)
#     version = models.CharField(max_length=100, blank=True, help_text="版本", default="0.0.1")

class Input(models.Model):
    id = models.AutoField(primary_key=True)
    tool = models.ForeignKey(Tool)
    identifier = models.CharField(max_length=250)
    ref_mark = models.BooleanField(default=False)
    ref_file = models.CharField(max_length=500, default="", null=True, blank=True)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    list = models.BooleanField(default=False, blank=True)
    list_cols = models.CharField(max_length=250, blank=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.identifier


class Param(models.Model):
    id = models.AutoField(primary_key=True)
    tool = models.ForeignKey(Tool)
    identifier = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=250, choices=[("string", "string"), ("integer", "integer"), ("real", "real"), ("boolean","boolean"),("enum","enum")])
    enum_value = models.CharField(max_length=500,null=True, default="") # [(1,1,1),(2,2,2),(3,3,3)]
    min_value = models.FloatField(blank=True,null=True )
    max_value = models.FloatField(blank=True, null=True )
    default = models.CharField(max_length=250, blank=True)
    required = models.BooleanField(default=True,blank=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.identifier


class Output(models.Model):
    id = models.AutoField(primary_key=True)
    tool = models.ForeignKey(Tool)
    identifier = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    required = models.BooleanField(default=True)
    list = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)

    outdir = models.CharField(max_length=500,blank=True)
    # src = models.CharField(max_length=250,blank=True)
    # delimeter = models.CharField(max_length=10, default=".", blank=True)
    pattern = models.CharField(max_length=1000, help_text="", blank=True)
    deleted = models.BooleanField(default=False)

    def __unicode__(self):
        return self.identifier




