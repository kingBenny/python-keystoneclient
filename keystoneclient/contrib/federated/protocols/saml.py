# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import BaseHTTPServer
from keystoneclient import exceptions as federated_exceptions
import os
import ssl
import webbrowser

## Sends the authentication request to the IdP along
# @param idpEndpoint The IdP address
# @param idpRequest The authentication request returned by Keystone
def getIdPResponse(idpEndpoint, idpRequest, realm=None):


    global response
    response = None
    config = open(os.path.join(os.path.dirname(__file__),
                  "config/federated.cfg"), "Ur")
    line = config.readline().rstrip()
    key = ""
    cert = ""
    timeout = 300
    while line:
        if line.split('=')[0] == "KEY":
            key = line.split("=")[1].rstrip()

        if line.split("=")[0] == "CERT":
            cert = line.split("=")[1].rstrip()
        if line.split('=')[0] == "TIMEOUT":
            timeout = int(line.split("=")[1])
        line = config.readline().rstrip()
    config.close()
    if key == "default":
        key = os.path.join(os.path.dirname(__file__), "certs/server.key")
    if cert == "default":
        cert = os.path.join(os.path.dirname(__file__), "certs/server.crt")
    print('Initiating Authentication against: ' + realm['name'] + '\n')
    webbrowser.open(idpEndpoint + idpRequest)
    class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

        def log_request(code=0, size=0):
            return

        def log_error(format="", msg=""):
            return

        def log_request(format="", msg=""):
            return

        def do_POST(self):
            global response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            varLen = int(self.headers["Content-Length"])
            #response = urlparse.parse_qs(self.rfile.read(varLen))
            response = self.rfile.read(varLen)
            if response is None:
                self.wfile.write("An error occured.")
                raise federated_exceptions.CommunicationsError()
            self.wfile.write("You have successfully logged in. "
                             "You can close this window now.")
    httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), RequestHandler)
    try:
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=key,
                       certfile=cert, server_side=True)
        httpd.socket.settimeout(1)
    except BaseException as e:
        print(e.value)
    count = 0
    while response is None and count < timeout:
        try:
            httpd.handle_request()
            count = count + 1
        except Exception as e:
            print(e.value)
    if response is None:
        print('There was no response from the Identity Provider +\
               or the request timed out')
        exit("An error occurred, please try again")
    print("Authentication Complete\n")
    return response
