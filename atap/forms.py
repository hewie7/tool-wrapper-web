# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User
import bootstrap_toolkit
from bootstrap_toolkit.widgets import *
from django.forms import ModelForm
from atap.models import Tool, Input, Param, Output

def validate_name(value):
    if value[0].isdigit():
        raise forms.ValidationError("must not start with numbers")


def validate_pattern(value):
    if "*" in value:
        pass
    elif ";" in value:
        pass
    elif "prefix:" in value:
        pass
    elif "inputs" in value or "outputs" in value:
        pass
    elif "." in value:
        pass
    else:
        raise forms.ValidationError("Enter a valid value")


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label="User Name",
        error_messages={'required': 'User Name is empty'},
        widget=forms.TextInput(
            attrs={
                'placeholder': "User Name",
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label=u"Password",
        error_messages={'required': 'PassWord is empty'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'PassWord',
            }
        ),
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"User and Password cannot be empty")
        else:
            cleaned_data = super(LoginForm, self).clean()


class ChangepwdForm(forms.Form):
    oldpassword = forms.CharField(
        required=True,
        label=u"old",
        error_messages={'required': 'input your old password'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': "old password",
            }
        ),
    )
    newpassword1 = forms.CharField(
        required=True,
        label="new",
        error_messages={'required': 'input new password'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': "input new password",
            }
        ),
    )
    newpassword2 = forms.CharField(
        required=True,
        label=u"confirm",
        error_messages={'required': 'confirm new password'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': "confirm",
            }
        ),
     )
    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"cannot be empty")
        elif self.cleaned_data['newpassword1'] <> self.cleaned_data['newpassword2']:
            raise forms.ValidationError(u"The two input password is not consistent")
        else:
            cleaned_data = super(ChangepwdForm, self).clean()
        return cleaned_data

# class ToolForm(forms.ModelForm):
#     class Meta:
#         model = Tool


class ToolForm(forms.Form):
    name = forms.SlugField(
        label="Tool Name",
        min_length=3,
        validators=[validate_name],
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. BWA"
            }
        ),
        help_text="your tool name, combine with number, letters and underscores"
    )

    program = forms.CharField(
        label="Program",
        validators=[validate_name],
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. bwa.pl"
            }
        ),
        help_text="executable program file name"

    )

    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder':"Add some description here",
                'row': 5,
                'style': 'width:100%',
            }
        )
    )
    version = forms.CharField(
        label="Version",
    )

    mem = forms.IntegerField(
        label="Memory",
        initial=2000,
        help_text="Peak memory usage in megabytes (MB)."
    )

    cpu = forms.ChoiceField(
        label="CPU",
        choices=(
            ("require.CPU_NEGLIGIBLE", "CPU_NEGLIGIBLE"),
            ("require.CPU_SINGLE", "CPU_SINGLE"),
            ("require.CPU_ALL", "CPU_ALL"),
        ),
        initial="CPU_SINGLE",
        help_text="Possible values are: CPU_NEGLIGIBLE, CPU_SINGLE, CPU_ALL"
    )

    io = forms.ChoiceField(
        label="High IO",
        choices=[
            (True, "True"),
            (False, "False"),
        ],
        initial=False,
        help_text="Boolean, specify whether the tool is I/O-intensive."
    )

    disk_space = forms.IntegerField(
        label="Disk Space",
        initial=100,
        help_text="Disk space required, including input/output files, temporary files and the tool itself (GB)."
    )


    # def clean_name(self):
    #     name = self.cleaned_data['name']
    #     if len(name) < 3:
    #         raise forms.ValidationError("the name should be longer than 3")
    #     if name[0].isdigit():
    #         raise forms.ValidationError("the name must not start with number")
    #     if Tool.objects.get(name=name):
    #         raise forms.ValidationError("the name had be used")
    #     return name
    #
    # def clean_program(self):
    #     program = self.cleaned_data['program']
    #     if " " in program:
    #         raise forms.ValidationError("this should be an executable program file name")
    #     return program

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("Please correct the errors")

        cleaned_data = super(ToolForm, self).clean()
        return cleaned_data


# class InputForm(forms.ModelForm):
#     class Meta:
#         model = Input

class InputForm(forms.Form):
    identifier = forms.SlugField(
        min_length=2,
        label="identifier",
        widget=forms.TextInput(
            attrs={
                "placeholder": "variable name",
            }
        ),
        help_text="合法的变量名称",
        validators=[validate_name]
    )

    name = forms.CharField(
        label="name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "human-readable name "
            }
        ),
        help_text="任意名称",
    )

    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': "Add some description here",
                'row': 2,
                'style': 'width:80%',
            }
        )
    )

    required = forms.BooleanField(
        label=u"required",
        required=False,
        initial=True
    )

    list = forms.BooleanField(
        label=u"list",
        required=False,
        initial=False

    )
    ref_mark = forms.BooleanField(
        label="use pre-collected files",
        required=False,
        initial=False,
    )

    ref_file = forms.CharField(
        label="public resource name",
        required=False,
        widget=forms.TextInput(
        attrs={
        # "id": "xxxx",
        "placeholder": "choose from right panel", 
        "readonly": "readonly", })

    ) 

    # list_cols = forms.CharField(
    #     label="list columns",
    #     required=False,
    #     widget=forms.TextInput(
    #         attrs={
    #             "placeholder": "sample,path"
    #         }
    #     ),
    #     help_text="列表文件内容，只在输入文件是list时指定"
    #
    # )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("please correct the errors")
        else:
            cleaned_data = super(InputForm, self).clean()
        return cleaned_data



# class ParamForm(forms.ModelForm):
#     class Meta:

class ParamForm(forms.Form):
    identifier = forms.SlugField(
        label="identifier",
        min_length=2,
        validators=[validate_name]
    )

    name = forms.CharField(
        label="name",
    )

    description = forms.CharField(
        label="description",
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': "Add some description here",
                'row': 2,
                'style': 'width:80%',
            }
        ),
    )

    type = forms.ChoiceField(
        label="param type",
        choices=(
            ("string", "string"),
            ("integer", "integer"),
            ("real", "real"),
            ("boolean", "boolean"),
            ("enum", "enum"),
        ),
        initial="string",

    )
    required = forms.BooleanField(
        label="required",
        initial=True,
        required=False,
    )

    default = forms.CharField(
        label="default",
        required=False,
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("please correct the errors")
        else:
            cleaned_data = super(ParamForm, self).clean()
        return cleaned_data


class OutputForm(forms.Form):

    identifier = forms.SlugField(
        label="identifier",
        min_length=2,
        validators=[validate_name]
    )

    name = forms.CharField(
        label="name",
    )

    description = forms.CharField(
        label="description",
        required=False,
        widget=forms.Textarea(
            attrs={
                'placeholder': "Add some description here",
                'row': 2,
                'style': 'width:80%',
            }
        ),
    )

    required = forms.BooleanField(
        label="required",
        initial=True,
        required=False,

    )

    list = forms.BooleanField(
        label="list",
        initial=False,
        required=False,
    )

    archive= forms.BooleanField(
        label="archive folder",
        initial=False,
        required=False,
    )

    outdir = forms.CharField(
        label="output dir",
        required=True,
        initial = "./",
        widget=forms.TextInput(
            attrs={
                "placeholder": "./"
            }
        ),
    )

    # # src = forms.ChoiceField(
    #     label="source of output file name",
    #     choices=(),
    # )

    # src = forms.ModelChoiceField(
    #     label="src",
    #     queryset=(),
    # )

    # delimeter = forms.CharField(
    #     label="delimeter",
    #     initial=".",
    #     required=True,
    # )
    #

    # abc.txt (single)
    # {input->prefix}.bam (single)
    # {input->sample}.bam (single)
    # {input[0]->prefix}.bam (single)
    # {input->library}_{input->lane}.bam (single)
    # *.bam (list)
    # chr_*.bam (list)
    ###########################
    # multi- combination of above
    # abc.txt, cfd.txt (list)
    # abc.txt, *.bam (list)
    # {input->prefix}.bam, {input->sample}.bam (list)
    ##########################
    # replace
    # {element}
    # {element->method}
    # {elements->method}
    # {}_{



    pattern = forms.CharField(
        label="pattern",
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": """
    # the output notations:
    # plain name, wildcard(*),
    # {element}, {element[offset]},{element->method}.
    # or combinations of all above, seperated by comma
    # legal element are list in right panel
    ----------------------------------------------
    # abc.txt
    # *.bam (list)
    # chr_*.bam (list)
    # {param}.bam 
    # {input->prefix}.bam 
    # {input->sample}.bam
    # {input[0]->prefix}.bam
    # {input->library}_{input->lane}.bam
    ----------------------------------------------
                """,
                'row': 2,
                'style': 'width:80%',
            }
        ),
        validators=[validate_pattern],
        # validators=
    )

    # def clean_src(self):
    #     return self.cleaned_data['src']

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError("please correct the errors")
        else:
            cleaned_data = super(OutputForm, self).clean()
        return cleaned_data



