import datetime
import sys
import os
import re
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.db.models import Q

# Create your views here.
from django.shortcuts import render_to_response,render,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.template.context import RequestContext

from django.forms.formsets import formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# from bootstrap3.widgets import
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *
from .wrap import *
import subprocess
WD ="/rd/workspace/"


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('login.html', RequestContext(request, {'form': form,}))
    else:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect("/tools")
            else:
                return render_to_response('login.html', RequestContext(request, {'form': form, 'password_is_wrong': True}))
        else:
            return render_to_response('login.html', RequestContext(request, {'form': form, }))


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/accounts/login/")


@login_required
def changepwd(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render_to_response('changepwd.html', RequestContext(request, {'form': form,}))
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = auth.authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return HttpResponseRedirect(reverse('tool-list-page'))
            else:
                return render_to_response('changepwd.html', RequestContext(request, {'form': form,'oldpassword_is_wrong':True}))
        else:
            return render_to_response('changepwd.html', RequestContext(request, {'form': form,}))


@login_required
def list_tools(request):

    username = request.user.username
    query = request.GET.get('query')
    if query is not None:
        lines = Tool.objects.filter(Q(deleted=0), Q(name__icontains=query) | Q(program__icontains=query) | Q(description__icontains=query)
        #)
        | Q(author__username__icontains=query))
        #| Q(create_time__icontains=query) | Q(modify_time__icontains=query))
    else:
        lines = Tool.objects.filter(deleted=0).order_by("-id")
    paginator = Paginator(lines, 10)
    page = request.GET.get('page')
    # return HttpResponse("<h1>%s</h1>" % page)
    try:
        show_lines = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        show_lines = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        show_lines = paginator.page(paginator.num_pages)
    return render_to_response('tool_list.html', RequestContext(request, {'lines': show_lines, "user": username, "now":datetime.datetime.now(), }))


@login_required
def view_tool(request, tid):
    username = request.user.username
    tool = Tool.objects.get(id=tid)
    wd = os.path.join(WD, tool.author.username, tool.name)

    inputs = tool.input_set.all().filter(deleted=0)
    params = tool.param_set.all().filter(deleted=0)
    outputs = tool.output_set.all().filter(deleted=0)

    if request.method == "GET":
        return render_to_response('tool_view.html', RequestContext(
        request, {'wd':wd, 'tool':tool, 'inputs': inputs, 'params': params, 'outputs': outputs}))
    else:
        pass



@login_required
def add_tool(request):
    username = request.user.username
    if request.method == "GET":
        t_form = ToolForm(
            initial= {
                "version": "0.0.1",
            }
        )
        return render_to_response("tool.html", RequestContext(request, {'form': t_form}))
    else:
        t_form = ToolForm(request.POST)
        if t_form.is_valid():
            tool = Tool.objects.create(
                # name=request.POST.get("name", ""),
                # program=request.POST.get("program", ""),
                # description=request.POST.get("description", ""),
                # author=User.objects.get(username=username),
                # version=request.POST.get("version", "0.0.1"),
                # create_time=datetime.datetime.now(),
                # modify_time=datetime.datetime.now()
                name=t_form.cleaned_data.get("name"),
                program=t_form.cleaned_data.get("program"),
                description=t_form.cleaned_data.get("description"),
                author=User.objects.get(username=username),
                version=t_form.cleaned_data.get("version"),
                create_time=datetime.datetime.now(),
                modify_time=datetime.datetime.now(),
                io=t_form.cleaned_data.get("io"),
                cpu=t_form.cleaned_data.get("cpu"),
                mem=t_form.cleaned_data.get("mem"),
                disk_space=t_form.cleaned_data.get("disk_space"),
            )
            tool.save()
            # tool.id
            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool.id,)))
        else:
            return render_to_response("tool.html", RequestContext(request, {'form': t_form}))




@login_required
def modify_tool(request, tid):
    username = request.user.username
    tool = Tool.objects.get(id=tid)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))

    if request.method == "GET":
        t_form = ToolForm(
            initial={
                "name": tool.name,
                "program": tool.program,
                "description": tool.description,
                "version": tool.version,
                "io": tool.io,
                "cpu": tool.cpu,
                "mem": tool.mem,
                "disk_space": tool.disk_space,
            }
        )
        return render_to_response("tool.html", RequestContext(request, {"form": t_form,"state": tool.state}))
    else:
        t_form = ToolForm(request.POST)
        if t_form.is_valid():
            tool.name = t_form.cleaned_data.get("name")
            tool.program = t_form.cleaned_data.get("program")
            tool.description = t_form.cleaned_data.get("description")
            tool.version = t_form.cleaned_data.get("version")
            tool.modify_time = datetime.datetime.now()
            tool.io = t_form.cleaned_data.get("io")
            tool.cpu = t_form.cleaned_data.get("cpu")
            tool.mem = t_form.cleaned_data.get("mem")
            tool.disk_space = t_form.cleaned_data.get("disk_space")
            tool.save()
            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool.id,)))
        else:
            return render_to_response("tool.html", RequestContext(request, {'form': t_form}))

@login_required
def add_input(request, tool_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    refs = []
    #todo add reference here
    for line in os.popen("/usr/local/bin/list-refs"):
        line = line.strip()
        if "PRE" in line:
            continue
        refs.append(re.split("\s+", line)[-1])

    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))


    if request.method == 'GET':
        form = InputForm()
        return render_to_response("input.html", RequestContext(request, {"form": form, 'tool': tool, 'refs': refs}))
    else:
        form = InputForm(request.POST)
        if form.is_valid():
            input = Input.objects.create(
                tool=tool,
                identifier=form.cleaned_data.get("identifier"),
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description"),
                required=form.cleaned_data.get("required"),
                list=form.cleaned_data.get("list"),
                ref_mark=form.cleaned_data.get("ref_mark", False),
                ref_file=form.cleaned_data.get("ref_file", ""),
                # list_cols=form.cleaned_data.get("list_cols"),
            )
            input.save()

            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))

        else:
            return render_to_response("input.html",RequestContext(request, {"form": form,"tool":tool, "refs":refs}))

@login_required
def delete_input(request, tool_id, input_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    input = Input.objects.get(id=input_id)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))
    input.deleted = True
    input.save()

    return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))



@login_required
def modify_input(request, tool_id, input_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    input = Input.objects.get(id=input_id)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))
    refs = []
    #todo add reference here
    for line in os.popen("/usr/local/bin/list-refs"):
        line = line.strip()
        if "PRE" in line:
            continue
        refs.append(re.split("\s+", line)[-1])


    if request.method == 'GET':
        form = InputForm(
            initial={
                "identifier": input.identifier,
                "name": input.name,
                "description": input.description,
                "required": input.required,
                "list": input.list,
                "ref_mark": input.ref_mark,
                "ref_file": input.ref_file,
                # "list_cols": input.list_cols
            }
        )
        return render_to_response("input.html", RequestContext(request, {"form": form, "tool": tool, "refs":refs}))
    else:
        form = InputForm(request.POST)
        if form.is_valid():
            input.identifier = form.cleaned_data.get("identifier")
            input.name = form.cleaned_data.get("name")
            input.description = form.cleaned_data.get("description")
            input.required = form.cleaned_data.get("required", False)
            input.list = form.cleaned_data.get("list", False)
            input.ref_mark = form.cleaned_data.get("ref_mark",False)
            input.ref_file = form.cleaned_data.get("ref_file","")
            # input.list_cols = form.cleaned_data.get("list_cols")
            input.save()

            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))

        else:
            return render_to_response("input.html", RequestContext(request, {"form": form, "tool": tool, "refs":refs}))



@login_required
def add_param(request, tool_id):

    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))

    if request.method == 'GET':
        form = ParamForm()
        return render_to_response("param.html", RequestContext(request, {"form": form, 'tool': tool}))

    else:
        enum_value = None
        min_value = None
        max_value = None
        p_type = request.POST.get("type")
        if p_type == "enum":
            enum_v = request.POST.getlist("enum_valu")
            enum_n = request.POST.getlist("enum_name")
            enum_d = request.POST.getlist("enum_desc")
            enum_value = repr(zip(enum_v,enum_n, enum_d))
        elif p_type in ["integer","real"]:
            min_value = request.POST.get("integer_min",None)
            max_value = request.POST.get("integer_max",None)
            if min_value == "":
                min_value = None
            if max_value == "":
                max_value = None

    
        form = ParamForm(request.POST)
        if form.is_valid():
            param = Param.objects.create(
                tool=tool,
                identifier=form.cleaned_data.get("identifier"),
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description"),
                required=form.cleaned_data.get("required"),
                type=form.cleaned_data.get("type"),
                default=form.cleaned_data.get("default"),
                enum_value=enum_value,
                min_value=min_value,
                max_value=max_value,
            )
            param.save()

            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))

        else:
            return render_to_response("param.html", RequestContext(request, {"form": form, "tool": tool}))


@login_required
def modify_param(request, tool_id, param_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    param = Param.objects.get(id=param_id)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))

    enums = []
    #if param.type in ["integer","real"]:
    #    init["min"] = param.min_value,
    #    init["max"] = param.max_value
    if param.type in "enum":
        enums = eval(param.enum_value)
    #    init["enums"] = enums

    if request.method == 'GET':
        form = ParamForm(
            initial={
                "identifier": param.identifier,
                "name": param.name,
                "description": param.description,
                "required": param.required,
                "type": param.type,
                "default": param.default,
            }
        )
        return render_to_response("param.html", RequestContext(request, {"form": form, "tool": tool,'param':param, 'enums':enums}))
    else:
        enum_value = None
        min_value = None
        max_value = None
        p_type = request.POST.get("type")
        if p_type == "enum":
            enum_v = request.POST.getlist("enum_valu")
            enum_n = request.POST.getlist("enum_name")
            enum_d = request.POST.getlist("enum_desc")
            enum_value = repr(zip(enum_v,enum_n, enum_d))
        elif p_type in ["integer","real"]:
            min_value = request.POST.get("integer_min")
            max_value = request.POST.get("integer_max")

        if min_value == "":
            min_value = None
        if max_value == "":
            max_value = None

        form = ParamForm(request.POST)
        if form.is_valid():
            param.identifier = form.cleaned_data.get("identifier")
            param.name = form.cleaned_data.get("name")
            param.description = form.cleaned_data.get("description")
            param.required = form.cleaned_data.get("required", False)
            param.type = form.cleaned_data.get("type")
            param.default = form.cleaned_data.get("default")
            param.enum_value = enum_value
            param.min_value = min_value
            param.max_value = max_value
            param.save()

            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))

        else:
            return render_to_response("param.html", RequestContext(request, {"form": form, "tool": tool}))


@login_required
def delete_param(request, tool_id, param_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    param = Param.objects.get(id=param_id)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))
    param.deleted = True
    param.save()

    return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))



@login_required
def add_output(request, tool_id):

    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    inputs = tool.input_set.all().filter(deleted=0)
    params = tool.param_set.all().filter(deleted=0)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))

    choice=[]
    choice.append(("*","*"))
    choice.append(("prefix","prefix"))
    choice.append(("sample","sample"))
    choice.append(("library","library"))
    choice.append(("lane","lane"))
    for i in inputs:
        choice.append(("%s" % i.identifier, "%s" % i.name))
    for p in params:
        choice.append(("%s" % p.identifier, "%s" % p.name))

    if request.method == 'GET':
        form = OutputForm()

        return render_to_response("output.html", RequestContext(request, {"form": form, 'tool': tool, 'choices': choice}))

    else:
        form = OutputForm(data=request.POST)
        if form.is_valid():
            output = Output.objects.create(
                tool=tool,
                identifier=form.cleaned_data.get("identifier"),
                name=form.cleaned_data.get("name"),
                description=form.cleaned_data.get("description"),
                required=form.cleaned_data.get("required"),
                list=form.cleaned_data.get("list"),
                archive=form.cleaned_data.get("archive",False),
                # src=request.POST.get("src"),
                # delimeter=form.cleaned_data.get("delimeter"),
                # pattern=form.cleaned_data.get("pattern"),
                outdir=request.POST.get("outdir","./"),
                # src=request.POST.get("src",""),
                # delimeter=request.POST.get("delimeter", "."),
                pattern=request.POST.get("pattern")
            )
            output.save()

            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))

        else:
            return render_to_response("output.html", RequestContext(request, {"form": form, "tool": tool, "choices":choice}))


@login_required
def modify_output(request, tool_id, output_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    output = Output.objects.get(id=output_id)
    inputs = tool.input_set.all().filter(deleted=0)
    params = tool.param_set.all().filter(deleted=0)

    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))
    choice=[]
    choice.append((".","."))
    choice.append(("*","*"))
    choice.append(("prefix","prefix"))
    choice.append(("sample","sample"))
    choice.append(("library","library"))
    choice.append(("lane","lane"))
    
    for i in inputs:
        choice.append(("%s" % i.identifier, "%s" % i.name))
    for p in params:
        choice.append(("%s" % p.identifier, "%s" % p.name))

    if request.method == 'GET':
        form = OutputForm(
            initial={
                "identifier": output.identifier,
                "name": output.name,
                "description": output.description,
                "required": output.required,
                "list": output.list,
                "outdir": output.outdir,
                "archive": output.archive,
                # "delimeter": output.delimeter,
                "pattern": output.pattern,
            }
        )
        return render_to_response("output.html", RequestContext(request, {"form": form, "tool": tool,"output":output, "choices":choice}))
    else:
        form = OutputForm(request.POST)
        if form.is_valid():
            output.identifier = form.cleaned_data.get("identifier")
            output.name = form.cleaned_data.get("name")
            output.description = form.cleaned_data.get("description")
            output.required = form.cleaned_data.get("required", False)
            output.list = form.cleaned_data.get("list",False)
            output.outdir = request.POST.get("outdir","./")
            output.archive= request.POST.get("archive",False)
            # output.delimeter = request.POST.get("delimeter", ".")
            output.pattern = request.POST.get("pattern")
            output.save()

            return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))

        else:
            return render_to_response("output.html", RequestContext(request, {"form": form, "tool": tool}))

@login_required
def delete_output(request, tool_id, output_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    output = Output.objects.get(id=output_id)

    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))

    output.deleted =True
    output.save()
    return HttpResponseRedirect(reverse("tool-detail-page", args=(tool_id,)))


@login_required
def init(request, tool_id):
    username = request.user.username
    tool = Tool.objects.get(id=tool_id)
    author = tool.author.username
    if username != author:
        return render_to_response("401.html", RequestContext(request))

    user_space = os.path.join(WD, username)
    wd = os.path.join(WD, author,tool.name)
    if tool.state == "pending": 
        if not os.path.exists(wd):
            os.makedirs(wd)
        os.chdir(user_space)
        subprocess.check_call("/usr/local/bin/l3 init %s" % tool.name, shell=True)
    code_generator(wd, tool.id)
    build_skeleton(wd, tool.id)

    tool.state = "inited"
    tool.save()

    return render_to_response("init.html", RequestContext(request, {"tool":tool}))
    #return HttpResponse("""<script type="text/JavaScript">alert("SUCCESS"); </script>""")


@login_required
def delete_tool(request,tid):
    username = request.user.username
    tool = Tool.objects.get(id=tid)
    if tool.author.username != username:
        return render_to_response("401.html", RequestContext(request))

    wd = os.path.join(WD, tool.author.username,tool.name)
    subprocess.check_call("rm -rf %s" % wd, shell=True)

    tool.deleted = True
    tool.save()
    return HttpResponseRedirect(reverse("tool-list-page"))


def test(request):

    return render_to_response("test.html",RequestContext(request,{}))
