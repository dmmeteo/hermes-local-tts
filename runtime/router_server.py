#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

STATE = Path.home()/'.config/hermes-local-tts/mode'
TARGETS={'fast':'http://127.0.0.1:8767','quality':'http://127.0.0.1:8768'}
LOCK=Lock()
def mode():
 try: value=STATE.read_text().strip()
 except OSError: value='fast'
 return value if value in TARGETS else 'fast'
def health(url,timeout=1.5):
 try:
  with urllib.request.urlopen(url+'/health',timeout=timeout) as r:return bool(json.loads(r.read()).get('ready'))
 except Exception:return False
def wait_health(url,seconds=300):
 end=__import__('time').monotonic()+seconds
 while __import__('time').monotonic()<end:
  if health(url,2):return True
  __import__('time').sleep(1)
 return False
def switch(value):
 if value not in TARGETS: raise ValueError('mode must be fast or quality')
 units=['hermes-local-tts-fast.service'] if value=='fast' else ['hermes-local-tts-quality.service','hermes-local-tts-english.service']
 stop=['hermes-local-tts-quality.service','hermes-local-tts-english.service'] if value=='fast' else ['hermes-local-tts-fast.service']
 subprocess.run(['systemctl','--user','enable','--now',*units],check=True,timeout=30)
 if not wait_health(TARGETS[value]):
  subprocess.run(['systemctl','--user','disable','--now',*units],check=False,timeout=30)
  raise RuntimeError(f'{value} backend did not become ready')
 STATE.parent.mkdir(parents=True,exist_ok=True);tmp=STATE.with_suffix('.tmp');tmp.write_text(value+'\n');os.replace(tmp,STATE)
 subprocess.run(['systemctl','--user','disable','--now',*stop],check=False,timeout=30)
 return value
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path not in {'/health','/mode'}:self.send_error(404);return
  value=mode();self.send_json({'ready':health(TARGETS[value]),'mode':value,'target':TARGETS[value]})
 def do_POST(self):
  try:
   body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))))
   if self.path=='/mode':
    with LOCK:value=switch(str(body.get('mode','')))
    self.send_json({'mode':value,'ready':health(TARGETS[value],90)});return
   if self.path!='/v1/audio/speech':self.send_error(404);return
   value=mode();req=urllib.request.Request(TARGETS[value]+self.path,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=900) as r:payload=r.read();ctype=r.headers.get('Content-Type','audio/ogg')
   self.send_response(200);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
  except Exception as e:self.send_json({'error':str(e)},400)
 def log_message(self,*args):pass
 def send_json(self,value,status=200):
  p=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(p)));self.end_headers();self.wfile.write(p)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
