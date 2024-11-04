#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

import os
import asyncio
import threading
import json
import math
import time
import base64
import queue
import signal
import sys, os, getopt
import subprocess
import traceback
import random as rd
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

solana_API_url = "https://api.mainnet-beta.solana.com"

isExitSignal = False

def call_solana_api(cmd_msg_txt):
    timeout_counter = 1
    cmd_req = json.loads(cmd_msg_txt)

    while not isExitSignal:
        try:
            cmd_res = requests.post(solana_API_url, json = cmd_req)
            print(cmd_res.text)
            return cmd_res.text
        except Exception as e:
            logmsg = "Solana api Rate limited, wait for {0} seconds to retry...".format(timeout_counter)
            print(logmsg)

            time.sleep(timeout_counter)
            timeout_counter += 1
            if timeout_counter > 6:
                timeout_counter = 6
        
class ServerHandler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "content-type,solana-client,X-Requested-With")
        self.end_headers()

    def do_OPTIONS(self):
        print("OPTIONS request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))

        self.send_response(200, "ok")
        self._set_headers()

    def do_GET(self):
        print("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        
        self.send_response(200)
        self._set_headers()

        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        
        #print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
        #        str(self.path), str(self.headers), post_data.decode('utf-8'))

        msg_txt = post_data.decode('utf-8')
        logmsg = "POST data={0}".format(msg_txt)
        print(logmsg)

        cmd_res_text = call_solana_api(msg_txt)

        self.send_response(200)
        self._set_headers()

        self.wfile.write(cmd_res_text.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=ServerHandler, port=8080):
    global httpd

    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('Stopping httpd...\n')

async def main_task():
    run()
    print("main task stopped!")

def exit_app(signum, frame):
    global isExitSignal

    print("get exit_app signal...")
    isExitSignal = True

    httpd.server_close()

    if api_server_task:
        api_server_task.cancel()

    loop.stop()
    print("exit process done!")
    #loop.call_soon_threadsafe(loop.stop)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_app)
    signal.signal(signal.SIGTERM, exit_app)
    #signal.signal(signal.SIGHUP, exit_app)

    """
    myobj = "{\"method\":\"getAccountInfo\",\"jsonrpc\":\"2.0\",\"params\":[\"BKziCKQawwqArkhdWBY7mbLPQaW9Rae9SdqS1dpM6iGD\",{\"encoding\":\"base64\"}],\"id\":\"86059d0d-ea62-498e-afab-544c125562e6\"}"
    jreq = json.loads(myobj)
    x = requests.post(solana_API_url, json = jreq)
    print(x.text)
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop = asyncio.get_event_loop()

    api_server_task = loop.create_task(main_task())

    try:
        loop.run_forever() # this is missing
        # loop.run_until_complete(try_task)
    except Exception as e:
        print("Exception loop:", e)
        print(traceback.print_exc())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

