#!/usr/bin/env python3
from __future__ import annotations
import io,json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from threading import Lock
import numpy as np,soundfile as sf
from supertonic import TTS
ENGINE=TTS(auto_download=True);STYLE=ENGINE.get_voice_style('M3');LOCK=Lock()
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path!='/health':self.send_error(404);return
  self.json({'ready':True,'mode':'fast','backend':'supertonic-3','voice':'M3/Robert','steps':16})
 def do_POST(self):
  try:
   if self.path!='/v1/audio/speech':self.send_error(404);return
   b=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))));text=str(b.get('text','')).strip()
   if not text:raise ValueError('text is required')
   with LOCK:wav,_=ENGINE.synthesize(text,voice_style=STYLE,total_steps=16,speed=1.05)
   out=io.BytesIO();sf.write(out,np.asarray(wav).squeeze(),ENGINE.sample_rate,format='WAV');p=out.getvalue();self.send_response(200);self.send_header('Content-Type','audio/wav');self.send_header('Content-Length',str(len(p)));self.end_headers();self.wfile.write(p)
  except Exception as e:self.json({'error':str(e)},400)
 def log_message(self,*args):pass
 def json(self,v,s=200):
  p=json.dumps(v).encode();self.send_response(s);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(p)));self.end_headers();self.wfile.write(p)
if __name__=='__main__':ThreadingHTTPServer(('127.0.0.1',8767),Handler).serve_forever()
