import sys
import os
from .models import *
import re
import json

CODE_INDENT_INDEX = 0
WHITE_SPACE = " " * 4
MULTI_LINE_SEP = '^'

#DEBUG = True
DEBUG =False


def compose(f=sys.stdout, snippets="", indent=False, retract=False, newline=True, interval=1):
    global CODE_INDENT_INDEX
    assert not(indent and retract)

    codes = snippets.split(MULTI_LINE_SEP)
    if indent:
        CODE_INDENT_INDEX = CODE_INDENT_INDEX + 1
    if retract:
        CODE_INDENT_INDEX = CODE_INDENT_INDEX - 1

    whitespaces = CODE_INDENT_INDEX * WHITE_SPACE

    for index in range(len(codes)):
        if index >= 1:
            f.write("\n")
        f.write(whitespaces + codes[index])

    if newline:
        f.write("\n"*interval)


def code_generator(wd, tool_id):
    global CODE_INDENT_INDEX
    CODE_INDENT_INDEX = 0
    tool = Tool.objects.get(id=tool_id)
    inputs = tool.input_set.all().filter(deleted=0, ref_mark=0)
    references = tool.input_set.all().filter(deleted=0, ref_mark=1)
    params = tool.param_set.all().filter(deleted=0)
    outputs = tool.output_set.all().filter(deleted=0)

    if DEBUG:
        f = sys.stdout
    else:
        wrapper_name = tool.name.lower() + ".py"
        f = open(os.path.join(wd, tool.name.lower(), wrapper_name),"w")

    compose(f, "import os")
    compose(f, "import sys")
    compose(f, "import glob")
    compose(f, "import re")
    compose(f, "from compiler.ast import flatten")
    compose(f, "from l3sdk import define, Process,require", interval=2)
    compose(f, "@require(mem_mb=%s, cpu=%s, high_io=%s)" % (tool.mem, tool.cpu, bool(tool.io)), interval=3)

    compose(f, "class %s(define.Wrapper):" % tool.name.upper())

    # construct look up dict
    lookup = {}

    # default inherit this meta
    inherit_meta = {}

    # inputs
    if len(inputs) > 0:
        inherit_meta['none'] = inputs[0].identifier
        compose(f, 'class Inputs(define.Inputs):', indent=True)
        compose(f, indent=True)
        for i in inputs:
            lookup[i.identifier] = "self.inputs.%s" % i.identifier
            i.description = i.description.replace(r"\r", "")
            define_str = """%s = define.input(name=\"\"\"%s\"\"\", description=\"\"\"%s\"\"\", required=%s, list=%s)""" % \
                         (i.identifier, i.name, i.description, bool(i.required), bool(i.list))
            compose(f, define_str)
    else:
        compose(f, 'class Inputs(define.Inputs):', indent=True)
        compose(f, indent=True)
        compose(f, "pass")

    # reference
    if len(references) >0:
        compose(f, "", retract=True)
        compose(f, 'class Reference(define.References):', indent=True)
        compose(f, indent=True)
        for r in references:
            define_str = """%s = define.reference(name="%s", links="s3://bgionline-tool-refs/%s",list=False""" % (r.identifier, r.name, r.ref_file)
            compose(f, define_str)

    # outputs
    if len(outputs) > 0:
        compose(f, "", retract=True)
        compose(f, 'class Outputs(define.Outputs):')
        compose(f,indent=True)
        for o in outputs:
            lookup[o.identifier] = "self.outputs.%s" % o.identifier
            o.description = o.description.replace(r"\r","")
            define_str = """%s = define.output(name=\"\"\"%s\"\"\", description=\"\"\"%s\"\"\", required=%s, list=%s)""" % \
                         (o.identifier, o.name, o.description, bool(o.required), bool(o.list))
            compose(f, define_str)
    else:
        compose(f, 'class Output(define.Outputs):')
        compose(f, indent=True)
        compose(f, "pass")

    # params
    compose(f, "", retract=True)
    if len(params) > 0:
        compose(f, 'class Params(define.Params):')
        compose(f, indent=True)
        for p in params:
            lookup[p.identifier] = "self.params.%s" % p.identifier
            p.description = p.description.replace(r"\r", "")
            default = ""
            if p.type == "string":
                default = """'%s'""" % p.default
            elif p.type == "boolean":
                if p.default in "True,true,False,false":
                    default = p.default.capitalize()
                else:
                    default = bool(p.default)
            else:
                default = p.default
            if p.type == "enum":
                define_str = """%s = define.%s(%s, name=\"\"\"%s\"\"\", description=\"\"\"%s\"\"\", required=%s, default= '%s')""" % \
                         (p.identifier, p.type, p.enum_value, p.name, p.description, bool(p.required), default)
            elif p.type in ["integer","real"]:
                plugin = []
                if p.min_value is not None:
                    if p.type == "integer":
                        p.min_value = int(p.min_value)
                    plugin.append("min=%s" % p.min_value)
                if p.max_value is not None:
                    if p.type == "integer":
                        p.max_value = int(p.max_value)
                    plugin.append("max=%s" % p.max_value)
                define_str = """%s = define.%s(name=\"\"\"%s\"\"\", description=\"\"\"%s\"\"\", required=%s, default= '%s', %s)""" % (p.identifier, p.type, p.name, p.description, bool(p.required), default, ",".join(plugin))

            else:
                define_str = """%s = define.%s(name=\"\"\"%s\"\"\", description=\"\"\"%s\"\"\", required=%s, default= %s)""" % \
                         (p.identifier, p.type, p.name, p.description, bool(p.required), default)

            compose(f, define_str)
    else:
        compose(f, 'class Params(define.Params):')
        compose(f, indent=True)
        compose(f, "pass")

    # execute
    compose(f, "", retract=True)
    compose(f, "def execute(self):")

    # config.txt
    compose(f, """config = open("__config__.txt", "w")""", indent=True)
    compose(f, """config.write("#<cfg>\\n")""")
    # $inputs
    if len(inputs) > 0:
        compose(f, """config.write("\\n[input]\\n")""")
        for i in inputs:
            i.description = i.description.replace(r"\r","")
            if i.list:
                compose(f, """# convert %s to list file""" % i.identifier)
                compose(f, """list_file = open("__%s__.list","w")""" % i.identifier)
                compose(f, """for i in self.inputs.%s:""" % i.identifier)
                # metas
                compose(f, """fields = [ "%s:%s" % (k,v) for k,v in i.meta.items()]""", indent=True)
                compose(f, """list_file.write("%s\\t%s\\n" % (i, ','.join(fields)))""")
                compose(f, """config.write("%s=__%s__.list\\n")""" % (i.identifier, i.identifier), retract=True)
                compose(f, """list_file.close()""")
                #compose(f, retract=True)
            else:
                compose(f, """%s_meta = ','.join(['%%s:%%s' %% (k,v) for k,v in self.inputs.%s.meta.items()])""" % (i.identifier, i.identifier))
                compose(f, """config.write("%s=%%s\\t %%s\\n" %% (self.inputs.%s, %s_meta ))""" % (i.identifier, i.identifier, i.identifier))

    # references
    if len(references) > 0:
        compose(f, """config.write("\\n[reference]\\n")""")
        compose(f, """config.write("%s=./database/%s/")""" % (r.identifier, r.identifier))

    # $params
    if len(params) > 0:
        compose(f, """config.write("\\n[params]\\n")""")
        for p in params:
            p.description = p.description.replace(r"\r", "")
            compose(f, """config.write("%%s=%%s\\n" %% ('%s', self.params.%s))""" % (p.identifier, p.identifier))

    # $outputs
    compose(f, "")
    ###########################
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
    # {}_{}

    def trans(out_dir="./", patterns=""):
        #out_dir += "/"
        segments = [i.strip() for i in patterns.split(",") if i.strip() != ""]
        if len(segments) == 0:
            return ["ERROR: empty pattern string"]
        else:
            meta = []
            for index in range(len(segments)):
                metadata = None
                pattern = segments[index]
                template = os.path.join(out_dir,re.sub("{[^{}]+}", "%s", pattern))

                m = re.findall(r"{(\w+)(\[\d\])?(->)?(\w*)}", pattern)
                if len(m) == 0:
                    if "*" in pattern:
                        segments[index] = "glob.glob('%s')" % os.path.join(out_dir, pattern)
                        metadata = "*"
                    else:
                        segments[index] = "'%s'" % os.path.join(out_dir, pattern)
                else:
                    muts = []
                    for ix, (element, offset, sign, method) in enumerate(m):
                        mut = ""
                        if element == "":
                            return "ERROR: no element in {} pattern"
                        else:
                            mut += lookup.get(element, "NA")
                            # inherit meta
                            if "self.inputs" in lookup.get(element, "NA"):
                                metadata = element
                        if offset != "":
                            mut += offset
                            metadata = element + offset
                        if method == "prefix":
                            mut = "os.path.basename(%s).split('.')[0]" % mut
                        elif method != "":
                            mut = "f('%s', %s.meta)" % (method, mut)
                        else:
                            mut = mut
                        muts.append(mut)
                    segments[index] = "'%s' %% (%s)" % (template, ",".join(muts))
                meta.append(metadata)

        return segments, meta


    compose(f, """config.close()""", interval=3)

    for r in references:
        compose(f, """Process("tar","xvf", self.references.%s, "-C", "./database/%s/").run() """ % (r.identifier, r.identifier))

    compose(f, """Process("perl","/opt/bin/%s", "-conf", "__config__.txt", "-outdir", "./", stdout="__run__.sh").run()""" % tool.program)
    compose(f, """Process("sh","__run__.sh").run()""",interval=2)
    #compose(f,"""%s""" % json.dumps(inherit_meta) )

    # append config.txt, claim output of script
    manifest = {}
    archive = []
    compose(f, """### case-insensitivly retrive metadata function""")
    compose(f, """f = lambda x,y: y.get(x.lower()) or y.get(x.upper()) or y.get(x.capitalize()) or 'NA'""")

    compose(f, """### claim scripts output ###""")
    compose(f, """config = open("__config__.txt", "a+")""")
    if len(outputs) > 0:
        compose(f, """config.write("\\n[outputs]\\n")""")
        for o in outputs:
            o.description = o.description.replace(r"\r", "")
            compose(f, "######## %s #######" % o.identifier)
            exprs, meta = trans(o.outdir, o.pattern)
            if len(exprs) == 1:
                if o.archive:
                    folder = o.outdir
                    name = exprs[0].replace("%s/" % folder,"")
                    compose(f, """%s_filename = %s""" % (o.identifier, name))
                    compose(f, """config.write("%s=%s\\n")""" % (o.identifier, folder))
                    archive.append((folder, o.identifier))
                else:
                    compose(f, """%s_filename = %s""" % (o.identifier, exprs[0]))
                    compose(f, """config.write("%s=%%s\\n" %% %s_filename)""" % (o.identifier, o.identifier))
                manifest[o.identifier] = "%s_filename" % o.identifier
                inherit_meta[o.identifier] = meta
            else:
                group_id = "%s_filename" % o.identifier
                compose(f, """%s = [] """ % group_id)
                for e in exprs:
                    compose(f, """%s.append(%s)""" % (group_id, e))
                compose(f,"""%s = flatten(%s)""" % (group_id, group_id))
                compose(f, """config.write("%s=%%s\\n" %% %s)""" % (o.identifier, group_id))
                manifest[o.identifier] = "%s_filename" % o.identifier
                inherit_meta[o.identifier] = meta


    compose(f, """config.close()""", interval=2)
    #archive file folder
    for folder, name in archive:
        compose(f, """Process("tar", "czf", %s_filename, '%s').run()""" % (name, folder), interval=2)
    #inherit metadata
    for k, v in manifest.items():

        compose(f, """self.outputs.%s = %s""" % (k, v))
        meta_vars = inherit_meta.get(k,None)
        if len(meta_vars) == 1:
            meta = meta_vars[0]
            if meta is None:
                compose(f, """self.outputs.%s.meta = self.inputs.%s.make_metadata()""" % (k, inherit_meta['none']) )
            elif meta == "*":
                compose(f, """for o in self.outputs.%s:""" % k)
                compose(f, """o.meta = self.inputs.%s.make_metadata()""" % inherit_meta['none'],indent=True) 
                compose(f, retract=True)
            else:
                compose(f, """self.outputs.%s.meta = self.inputs.%s.make_metadata()""" % (k, re.sub(r"\[\d\]","",meta)))
        else:
            for ix, meta in enumerate(inherit_meta[k]):
                compose(f, """self.outputs.%s[%s].meta = self.inputs.%s.make_metadata()""" % (k, ix, meta))
        compose(f, "")

    f.close()
    CODE_INDENT_INDEX = 0

#    return wrapper_file

def build_skeleton(wd, tool_id):
    tool = Tool.objects.get(id=tool_id)
    inputs = tool.input_set.all().filter(deleted=0)
    params = tool.param_set.all().filter(deleted=0)

    with open(os.path.join(wd, "description.txt"), "w") as desc:
        desc.write("%s\n" % tool.description.replace(r"\r\n",""))

    with open(os.path.join(wd, "push.sh"), "w") as desc:
        desc.write("l3 push %s %s $1\n" % (tool.name, tool.version))

    with open(os.path.join(wd, tool.name.lower(), "__init__.py"), "w") as init:
        init.write("from %s import %s\n" % (tool.name.lower(), tool.name.upper() ))

    with open(os.path.join(wd,"test.sh"),"w") as run:
        run.write("sudo rm -rf results && l3 run %s.%s input.json\n" % (tool.name.lower(), tool.name.upper()))

    if os.path.exists(os.path.join(wd,"input.json")):
                os.rename(os.path.join(wd,"input.json"), os.path.join(wd,"input.json.orig"))

    with open(os.path.join(wd, "input.json"), "w") as input_json:
        ins = {}
        pars = {}
        for i in inputs:
            if i.list:
                ins[i.identifier] = ["/l3bioinfo/test-data/","/l3bioinfo/test-data/"]
            else:
                ins[i.identifier] = "/l3bioinfo/test-data/"
        for p in params:
            default = ""
            if p.type == "string":
                default = """%s""" % p.default
            elif p.type == "boolean":
                if p.default in "True,true,False,false":
                    default = eval(p.default.capitalize())
                else:
                    default = bool(p.default)
            elif p.type == "integer":
                default = int(float(p.default))
            elif p.type == "real":
                default = float(p.default)
            else:
                default = p.default

            pars[p.identifier] = default

        content = {}
        content["$inputs"] = ins
        content["$params"] = pars
        s =json.dump(content, fp=input_json, indent=True)



