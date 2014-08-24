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
import federated_utils as futils
import json
from keystoneclient import exceptions
import os
import requests
import ssl
import sys
import urlparse
import webbrowser


def federatedAuthentication(keystone_endpoint, realm=None,
                            tenantFn=None, scoped=True):
    """Makes a number of server requests and builds the
    authorisation endpoint based on the users choice of
    IdP and Protocol. Once the user has specified a project
    the unscoped token can be exchanged for a scoped-token.
    """
    response = get_IdP_List(keystone_endpoint)
    if realm is None or {'name': realm} not in response['realms']:
        realm = select_IdP_and_protocol(keystone_endpoint, response)
    authentication_endpoint = keystone_endpoint + '/OS-FEDERATION' + \
        '/identity_providers/' + realm['IdP'] + \
        '/protocols/' + realm['protocol'] + '/auth'
    unscoped_token = get_unscoped_token(authentication_endpoint)
    if scoped:
        scoped_token = get_scoped_token(keystone_endpoint,
                                        unscoped_token, realm['protocol'])
        return json.loads(scoped_token.text), scoped_token
        '''the scoped_token.text is the body (lacking the ID) and the
        scoped_token is the entire server response, containing the header
        and therefore the iD.
        '''
    else:
        return unscoped_token


def select_IdP_and_protocol(keystone_endpoint, identity_providers):
    """Allows the user to choose an IdP and protocol from the list
    displayed to stdout. Makes calls to the keystone server to
    obtain the lists of IdPs and Protocols
    """
    if not identity_providers:
        raise exceptions.FederatedException('There are no available IdPs ' +
                                            'at the os-auth-url specified')
    print('\nPlease choose a service to authenticate with:')
    auth_options = []
    index = 0
    print('\t' + ('-' * 38))
    print('\tIndex\t| IdP\t\t| Protocol\t')
    print('\t' + ('-' * 38))
    for IdP in identity_providers['identity_providers']:
        protocol_list = get_protocol_List(keystone_endpoint, IdP)
        if not protocol_list:
            raise exceptions.FederatedException('There are no available ' +
                                                'protocols for the ' +
                                                'specified IdP')
        for protocol in protocol_list['protocols']:
            print('\t{ ' + str(index) + ' }\t  ' + IdP['id'] +
                  '\t\t  ' + protocol['id'])
            auth_options.append({'IdP': IdP['id'],
                                 'protocol': protocol['id']})
            index += 1
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(auth_options)) + ' }\t  Quit')
    print('\t' + ('-' * 38))
    choice = None
    while choice is None:
        try:
            choice = int(raw_input('Enter the number corresponding to' +
                                   ' the service you want to use: '))
        except Exception:
            print('An error occurred with your selection')
        if choice < 0 or choice > len(auth_options):
            print('The selection made was not a valid choice of service')
            choice = None
    if choice == len(auth_options):
        print('Quitting...')
        sys.exit(0)
    else:
        return auth_options[choice]


def get_IdP_List(keystone_endpoint):
    """targets the keystone server at the specified endpoint
    to obtain a list of IdPs
    """
    keystone_endpoint += '/OS-FEDERATION/identity_providers'
    resp = requests.get(keystone_endpoint)
    info = json.loads(resp.text)
    return info


def get_protocol_List(keystone_endpoint, realm):
    """processs the server response and extracts the protocol
    data.
    """
    #get and return a list of protocols for the specified IdP
    protocols = requests.get(realm['links']['protocols'])
    protocol_data = json.loads(protocols.text)
    return protocol_data


def get_unscoped_token(authentication_endpoint):
    """Tries to load a security certificate and creates an HTTP server
    to listen for the response in the browser. Captures the server
    response and redirects it to the localhost.
    """
    global response
    response = None
    #try to load certificate
    config = open(os.path.join(os.path.dirname(__file__),
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
    #the timeout read from the certificate file is far too long
    timeout = 20
    if key == "default":
        key = os.path.join(os.path.dirname(__file__),
                           "protocols/certs/server.key")
    if cert == "default":
        cert = os.path.join(os.path.dirname(__file__),
                            "protocols/certs/server.crt")
    #create the HTTP server
    httpd = BaseHTTPServer.HTTPServer(('localhost', 8080), RequestHandler)
    try:
        httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=key,
                                       certfile=cert, server_side=True)
        httpd.socket.settimeout(1)
    except BaseException as e:
        print(e.value)
    #handles our redirect to loalhost
    query_string = '?refer_to=localhost:8080&ssl=1'

    #open a browser and listen for a response
    webbrowser.open(authentication_endpoint + query_string)
    count = 0
    while response is None and count < timeout:
        try:
            httpd.handle_request()
            count = count + 1
        except Exception as e:
            print(e)
    if response is None:
        print('There was no response from the Identity Provider' +
              'or the request timed out')
        exit("An error occurred, please try again")
    print("Authentication Complete\n")
    return response[0]


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
        #BaseHTTPServer suppress output of token to user
        def log_message(self, format, *args):
            return

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
            parsed_path = urlparse.urlparse(self.path)
            params = {}
            try:
                params = urlparse.parse_qs(parsed_path.query)
            except Exception as e:
                print("e", e)
                response = None

            if params:
                if not params.get('token'):
                    response = None
                else:
                    response = params.get('token')
                    self.wfile.write("Authentication Complete. \n")
                    self.wfile.write("You can safely close this window.")

        def do_POST(self):
            self.do_GET()


def get_scoped_token(keystone_endpoint, unscoped_token, selected_protocol):
    """Exchanges the unscoped token for a token scoped to the specified
    project.
    """
    #get a list of available projects for the user
    project_endpoint = keystone_endpoint + '/OS-FEDERATION/projects'
    projects = requests.get(project_endpoint,
                            headers={'X-Auth-Token': unscoped_token})
    projects_list = json.loads(projects.text)
    chosen_project = futils.select_project(projects_list['projects'])
    #make the request for the scoped token
    scoped_token_endpoint = keystone_endpoint + '/auth/tokens'
    #needed in both header and body for correct authorisation
    body = json.dumps({'auth': {'identity': {'methods': [selected_protocol],
                                selected_protocol: {'id': unscoped_token}},
                                'scope': {'project':
                                {'id': chosen_project['id']}}}})
    scoped_token = requests.post(scoped_token_endpoint,
                                 headers={'Content-Type': 'application/json',
                                 'X-Auth-Token': unscoped_token},
                                 data=body)
    return scoped_token
