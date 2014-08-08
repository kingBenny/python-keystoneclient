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
from keystoneclient import exceptions
#import federated_exceptions as fe
import federated_utils as futils
import imp
import json
import os
import requests
import ssl
import sys
#import urllib2
import urlparse
import webbrowser
import time


def federatedAuthentication(keystoneEndpoint, realm=None, tenantFn=None, scoped=True):
    response = get_IdP_List(keystoneEndpoint)
    if realm is None or {'name': realm} not in response['realms']:
        realm = futils.selectRealm(response.get('identity_providers'))
    protocol_list = get_protocol_List(keystoneEndpoint, realm)
    selected_protocol = futils.selectProtocol(protocol_list['protocols'])
    authentication_endpoint = keystoneEndpoint + '/OS-FEDERATION/identity_providers/' + realm['id'] + '/protocols/' + selected_protocol['id'] + '/auth'
    unscoped_token = get_unscoped_token(authentication_endpoint)
    if scoped:
        scoped_token = get_scoped_token(keystoneEndpoint, unscoped_token, selected_protocol)
        return json.loads(scoped_token.text), scoped_token
        #the scoped_token.text is the body (lacking the ID) and the scoped_token is the entire server response, containing the header and 
        #therefore the iD.
    else:
        return unscoped_token        

def get_IdP_List(keystone_endpoint):
    keystone_endpoint += '/OS-FEDERATION/identity_providers'
    resp = requests.get(keystone_endpoint)
    info = json.loads(resp.text)
    return info

def get_protocol_List(keystone_endpoint, realm):
    #get and return a list of protocols for the specified IdP
    protocols = requests.get(realm['links']['protocols'])
    protocol_data = json.loads(protocols.text)
    return protocol_data

def get_unscoped_token(authentication_endpoint):
    global response
    response = None
    config = open(os.path.join(os.path.dirname(__file__),                   #<---------------try to load certificate
                  "protocols/config/federated.cfg"), "Ur")
    line = config.readline().rstrip()
    key = ""
    cert = ""
    while line:
        if line.split('=')[0] == "KEY":
            key = line.split("=")[1].rstrip()

        if line.split("=")[0] == "CERT":
            cert = line.split("=")[1].rstrip()
        if line.split('=')[0] == "TIMEOUT":
            timeout = int(line.split("=")[1])
        line = config.readline().rstrip()
    config.close()
    timeout = 20                        #<---------- the timeout read from the certificate file is far too long
    if key == "default":
        key = os.path.join(os.path.dirname(__file__), "protocols/certs/server.key")
    if cert == "default":
        cert = os.path.join(os.path.dirname(__file__), "protocols/certs/server.crt") 

    httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), RequestHandler)          #<---------------------HTTPServer
    try:
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=key,
                       certfile=cert, server_side=True)
        httpd.socket.settimeout(1)
    except BaseException as e:
        print(e.value)

    query_string = '?refer_to=localhost:8080&ssl=1'                             #<-----------handles our redirect to loalhost

    webbrowser.open(authentication_endpoint + query_string)                       #<--------------------------open browser
    count = 0
    while response is None and count < timeout:                             #<--------------------------listen for response
        try:
            httpd.handle_request()
            count = count + 1
        except Exception as e:
            print(e)
    if response is None:
        print('There was no response from the Identity Provider +\
               or the request timed out')
        exit("An error occurred, please try again")
    print("Authentication Complete\n")
    return response[0]

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
       
        #patched!
        def finish(self, *args, **kw):
            try:
                if not self.wfile.closed:
                    self.wfile.flush()
                    self.wfile.close()
            except socket.error:
                print("Socket Error: ", socket.error)
            self.rfile.close()

        def do_GET(self):
            global response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            parsed_path  = urlparse.urlparse(self.path)
            params = {}
            try:
                #params = dict([p.split('=') for p in parsed_path[4].split('&')])                   <---this is source of error
                params = urlparse.parse_qs(parsed_path.query)
            except Exception as e:
                print("e", e)
                response = None

            if params:
                if not params.get('token'):
                    response = None
                else:
                    response = params.get('token')
                    self.wfile.write("You have successfully logged in. "
                                "You can close this window now.")
        def do_POST(self):
            self.do_GET()
            
def get_scoped_token(keystone_endpoint, unscoped_token, selected_protocol):                            #<--------break down into separate functions!
    #get a list of available projects for the user
    project_endpoint = keystone_endpoint + '/OS-FEDERATION/projects' 
    projects = requests.get(project_endpoint, headers={'X-Auth-Token':unscoped_token})
    projects_list = json.loads(projects.text)
    chosen_project = futils.select_project(projects_list['projects'])
    #make the request for the scoped token
    scoped_token_endpoint = keystone_endpoint + '/auth/tokens'
    #needed in both header and body for correct authorisation
    body = json.dumps({'auth': {'identity':{'methods':[selected_protocol['id']], selected_protocol['id']:{'id':unscoped_token}},'scope':{'project':{'id': chosen_project['id']}}}})
    scoped_token = requests.post(scoped_token_endpoint, headers={'Content-Type': 'application/json', 'X-Auth-Token':unscoped_token}, data=body)
    return scoped_token
