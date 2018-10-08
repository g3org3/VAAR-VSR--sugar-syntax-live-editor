from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys
import json
import os
import epav
PORT = 5000

if os.environ.get('PORT'):
  try:
    p = int(os.environ.get('PORT'))
    print("> chaning port to :", p)
    PORT = p
  except:
    PORT = 5000

def res_send(content):
  if "text/html" in request.headers.get('Accept'): return "<pre>"+content+"</pre>"
  return content

app = Flask(__name__)
CORS(app)
def shell(line):
  try:
    output = subprocess.check_output(line.split(' '), stderr=subprocess.STDOUT)
    return output.strip()
  except subprocess.CalledProcessError as exc:
    return exc.output

"""------------------------------------
  CORE EXEC
------------------------------------"""
@app.route("/api/run", methods=["get", "options"])
def run_options():
  return ""

@app.route("/api/run", methods=["post"])
def run():
  data = request.get_json()['data']
  content = "-"
  try:
    content = epav.parseUserRules(data)
  except:
    content = data
  return res_send(content)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=PORT)
