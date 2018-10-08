import re
import md5
import smtlib

def dec2Bin(num):
  sym = "B"
  total = num
  if total > 999:
    sym = "KB"
    total = total / 1000
  if total > 999:
    sym = "MB"
    total = total / 1000
  if total > 999:
    sym = "GB"
    total = total / 1000
  if total > 999:
    sym = "TB"
    total = total / 1000
  if total > 999:
    sym = "PB"
    total = total / 1000
  return str(total) + " " + sym

def bin2Dec(rawBin):
  rawBin = str(rawBin).upper()
  if "MB" in rawBin:
    return str(int(rawBin.split("MB")[0]) * (10**6))
  if "GB" in rawBin:
    return str(int(rawBin.split("GB")[0]) * (10**9))
  if "KB" in rawBin:
    return str(int(rawBin.split("KB")[0]) * (10**3))
  if "TB" in rawBin:
    return str(int(rawBin.split("TB")[0]) * (10**12))
  if "PB" in rawBin:
    return str(int(rawBin.split("PB")[0]) * (10**15))
  if "B" in rawBin:
    return str(int(rawBin.split("B")[0]))
  return rawBin

def IP2Int(ip):
  o = map(int, ip.split('.'))
  res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
  return str(res)


def Int2IP(ipnum):
  o1 = int(ipnum / 16777216) % 256
  o2 = int(ipnum / 65536) % 256
  o3 = int(ipnum / 256) % 256
  o4 = int(ipnum) % 256
  return '%(o1)s.%(o2)s.%(o3)s.%(o4)s' % locals()

def experimental(rline):
  line = rline.split(';;- ')[1]
  tokens = line.split(' ')
  if len(tokens) is 2:
    return smtlib.declareVariable(tokens[0], tokens[1])
  if len(tokens) is 3 and not tokens[1] == "=":
    if len(tokens[2][1:].split(']')) is 2:
      return smtlib.declareArray(tokens[1], tokens[2][1:].split(']')[0])
    else:
      return smtlib.declareMatrix(tokens[1], tokens[2][1:].split(']')[0])
  if len(tokens) is 3 and tokens[1] == "=":
    if len(tokens[0].split('[')) is 1:
      return smtlib.assignVariable(None, tokens[0], tokens[2])
    else:
      i = tokens[0].split('[')[1].split(']')[0]
      return smtlib.assignToArray(tokens[0].split('[')[0], i, tokens[2])
  else:
    return rline

def preProcessor(line, MainData):
  if ";;-" in line:
    return experimental(line)
  if preProcessBytes(line):
    return preProcessBytes(line)
  elif preProcessIPs(line):
    return preProcessIPs(line)
  elif preProcessString(line, MainData):
    return preProcessString(line, MainData)
  return line

def preProcessIPs(line):
  try:
    pattern = re.compile(r"([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})")
    start = pattern.search(line).start()
    end = pattern.search(line).end()
    ipRaw = line[start:end]
    ipNumber = IP2Int(ipRaw)
    return pattern.sub(ipNumber, line)
  except:
    return False

def preProcessString(line, MainData):
  try:
    pattern = re.compile(r"\'.+\'")
    start = pattern.search(line).start()
    end = pattern.search(line).end()
    value = line[start+1:end-1]
    result = str(int(md5.new(value).hexdigest(), 16))
    MainData["stringsHashMap"][result] = value
    return pattern.sub(result, line)
  except:
    return False

def preProcessBytes(line):
  # detect bytes
  try:
    pattern = re.compile(r"(\d)+(\ )?(KB|MB|GB|TB|PB|B)")
    start = pattern.search(line).start()
    end = pattern.search(line).end()
    bytesRaw = line[start:end]
    bytesNumber = bin2Dec(bytesRaw)
    return pattern.sub(bytesNumber, line)
  except:
    return False

def findCustomTypesInUserRules(rawInput):
  customTypes = []
  for line in rawInput.split('\n'):
    if "deftype" in line:
      line = line.split(' ')
      if len(line) is 4:
        if line[0] == ";;" and line[1] == "deftype":
          customTypes.append({ "name": line[2], "type": line[3] })
      if len(line) is 3:
        if line[0] == ";;deftype":
          customTypes.append({ "name": line[1], "type": line[2] })
  return customTypes

def isTypeIP(value):
  value = value.strip()
  parts = value.split('.')
  if len(parts) is not 4:
    return False
  types = map(lambda x: type(x), parts)
  typesDict = {}
  for t in types:
    typesDict.setdefault(t, [])
    typesDict[t].append(t)
  if len(typesDict.keys()) is not 1:
    return False
  if len(typesDict[typesDict.keys()[0]]) is not 4:
    return False
  if typesDict[typesDict.keys()[0]][0] is not type(1):
    return False
  return True

def sugarSyntaxGetProperty(line, arrayName):
  # (< vmi.mem_size 4599)
  # into => (< (select (select vnfs x) "version") 4599)
  if (isTypeIP(line)):
    return line
  try:
    pattern = re.compile(r"([a-z]|[A-z]|_)+(\.([a-z]|[A-z]|_)+)+")
    start = pattern.search(line).start()
    end = pattern.search(line).end()
    att = line[start:end]
    parts = att.split('.')
    att = ".".join(parts[1:len(parts)])
    return pattern.sub("(select (select "+arrayName+" x) \""+att+"\")", line)
  except:
    return line

def getAttributesFromUserRules(rawRules):
  attList = []
  for line in rawRules.split('\n'):
    if "deftype" not in line:
      line = sugarSyntaxGetProperty(line, "")
    try:
      pattern = re.compile(r"\"(.+)\"")
      start = pattern.search(line).start()
      end = pattern.search(line).end()
      att = line[start+1:end-1]
      if not att in attList:
        attList.append(att)
    except:
      attList = attList
  return attList

def preStep(userRawRules):
  config = { "experimental": "1" }
  MainData = {
    "blob": "",
    "variables": {
      "names": [],
      "total": 0
    },
    "types": {
      "vnfs": "tosca.nodes.nfv.VNF",
      "vdus": "tosca.nodes.nfv.VDU",
      "vls": "tosca.nodes.nfv.VL",
      "cps": "tosca.nodes.nfv.CP",
      "fps": "tosca.nodes.nfv.FP",
      "vms": "tosca.nodes.Compute",
      "networks": "tosca.nodes.network.Network"
    },# ADD new array with your type here
    "sizes": {},
    # we generate this below
    # "sizes": {
    #   "vnfs": 0,
    #   "vdus": 0,
    #   "vls": 0,
    #   "cps": 0,
    #   "fps": 0,
    #   "vms": 0,
    #   "networks": 0,
    # },
    "nested": {},
    "stringsHashMap": {},
    "valueTypes": {},
    "rules": {
      "attributes": getAttributesFromUserRules(userRawRules)
    },
    "customTypes": findCustomTypesInUserRules(userRawRules),
    "nodes": {}
  }
  # add Custom Types
  for custom in MainData["customTypes"]:
    if MainData["types"].has_key(custom["name"]):
      MainData["types"][custom["name"]] = custom["type"]
    else:
      if config.has_key("experimental") and bool(config.get("experimental")):
        MainData["types"][custom["name"]] = custom["type"]
  
  # Generate Sizes
  for key in MainData["types"].keys(): MainData["sizes"][key] = 1
  return MainData

def parseUserRules(rawInput):
  MainData = preStep(rawInput)
  sizes = MainData["sizes"]
  inside_for = False
  invalid_for = True
  empty_for = False
  for_name = ""
  for_iterator_name = ""
  
  nested_inside_for = False
  nested_invalid_for = True
  nested_empty_for = False
  nested_for_name = ""
  nested_for_iterator_name = ""
  nested_content = ""

  smt2_extra_fors = ""

  validArrays = sizes.keys()
  smt2  = "\n\n;;------------------------\n"
  smt2 += ";;  USER Rules\n"
  smt2 += ";;------------------------\n"
  for line in rawInput.split('\n'):
    line = preProcessor(line, MainData)
    # print line, invalid_for, empty_for, inside_for
    if ";;endfor" in line:
      if nested_inside_for:
        nested_inside_for = False
        nested_invalid_for = True
        nested_empty_for = False
        prop_name = ".".join(nested_for_name.split('.')[1:len(nested_for_name.split('.'))])
        itername = nested_for_name.split('.')[0]
        transformed = map(transform, MainData["nested"].keys())
        arrays = filter(lambda x: x['prop_name'] == prop_name and x['itername'] == itername, transformed)
        correct_keys = map(lambda x: x['key'], arrays)
        for key in correct_keys:
          content = ""
          content += "(assert (forall ((y Int))\n"
          content += "  "+"(=>\n"
          content += "    "+"(and (< y " + key + "_size) (> y -1))\n"
          content += nested_content.replace(nested_for_iterator_name, "(select " + key + " y) ")
          content += "  "+")\n"
          content += "))"
          smt2_extra_fors += content+"\n"
      else:
        # print invalid_for
        if not invalid_for:
          smt2 += "  )\n"
          smt2 += "))\n\n"
        else:
          smt2 += line + "\n\n"
        inside_for = False
        invalid_for = True
        empty_for = False
    elif inside_for:
      if nested_inside_for:
        nested_content += line + "\n"
      elif ";;for " in line:
        nested_inside_for = True
        nested_for_name = line.split('in ')[1]
        nested_for_iterator_name = line.split("in ")[0].split(";;for ")[1].strip()
        nested_content = ""
      elif invalid_for:
        smt2 += ";;    " + line + "\n"
      elif for_iterator_name in line:
        # (< (select vmi "mem_size") 48)
        smt2 += "    " + line.replace(for_iterator_name, "(select " + for_name + " x) ") + "\n"
      else:
        # (< vmi.mem_size 48)
        line = sugarSyntaxGetProperty(line, for_name)
        smt2 += "    " + line + "\n"
    elif ";;for " in line:
      inside_for = True
      for_name = line.split("in ")[1]
      for_iterator_name = line.split("in ")[0].split(";;for ")[1]
      if for_name in validArrays:
        arraySize = sizes[for_name]
        invalid_for = arraySize < 1
        empty_for = arraySize < 1
        smt2 += line + " | size: "+str(arraySize)+"\n" if not empty_for else ""
      if not invalid_for:
        smt2 += "(assert (forall ((x Int))\n"
        smt2 += "  (=>\n"
        smt2 += "    (and (< x " + for_name + "_size) (> x -1))\n"
      else:
        if empty_for:
          smt2 += "\n;;Ignore rules, because no " + for_name + " descriptions where found!\n"
        else:
          smt2 += "\n;; invalid for, did not match array name: \"" + for_name +"\"\n"
        smt2 += line + "\n"
    else:
      smt2 += line + "\n"
  smt2 += smt2_extra_fors
  smt2 += ";;------ Done USER Rules ------\n\n"
  return smt2