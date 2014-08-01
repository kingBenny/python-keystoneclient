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
import ssl
import sys
#import urllib2
#import urlparse
import webbrowser


'''The super-function calls different API methods to obtain a scoped token.
keystone does not use scoped tokens, so this function can be called with 
scoped_token=False in order to use an unscoped token only.
@param keystoneEndpoint The keystone url
@param realm The IdP the user will be using
@param tenantFn The tenant friendly name the user wants to use
'''
def federatedAuthentication(keystoneEndpoint, realm=None, tenantFn=None, 
                            v3=False, scoped_token=True):
    response = getRealmList(keystoneEndpoint, v3)
    if realm is None or {'name': realm} not in response['realms']:
        if v3 == True:
            realm = futils.selectRealm(response.get('error').get('identity')
                                       .get('federated').get('providers'))
        else:
            realm = futils.selectRealm(response['realms'])
    request = getIdPRequest(keystoneEndpoint, realm, v3)
    # Load the correct protocol module according to the IdP type
    protocol = realm['type'].split('.')[1]
    processing_module = load_protocol_module(protocol)
    if not processing_module:
        sys.exit(1)
    if v3 == True:
        request = request.get('error').get('identity').get('federated')
        response = processing_module.getIdPResponse(request['endpoint'] + '?', request['data'], realm)
    else:
        response = processing_module.getIdPResponse(request['idpEndpoint'], request['idpRequest'], realm)
    tenantData, resp = getUnscopedToken(keystoneEndpoint, response, realm, v3)
    print('This is the tenant Data: ', tenantData)
    #we need these in the library for the ability to swap to a scoped token for a project 
    if scoped_token:
        tenant = futils.getTenantId(tenantData['tenants'], tenantFn)
        if tenant is None:
            tenant = futils.selectTenantOrDomain(tenantData['tenants'])
            if tenant.get("project", None) is None and tenant.get("domain", None) is None:
                tenant = tenant["id"]
                type = "tenantId"
            else:
                if tenant.get("domain", None) is None:
                    tenant = tenant["project"]["id"]
                    type = "tenantId"
                else:
                    tenant = tenant["domain"]["id"]
                    type = "domainId"
        scopedToken = swapTokens(keystoneEndpoint, tenantData['unscopedToken'], type, tenant, v3)
        return scopedToken
    else:
        if v3 == True:
            return tenantData, resp
        token = {}
        token['access'] = {}
        token['access']['token'] = tenantData['token']
        token['access']['serviceCatalog'] = []
        token['access']['user'] = tenantData['user']
         
        return token, None

def load_protocol_module(protocol):
    ''' Dynamically load correct module for processing authentication
        according to identity provider's protocol'''
    try:
        return imp.load_source(protocol, os.path.dirname(__file__)+'/protocols/'+protocol+'.py')
    except IOError as e:
        raise exceptions.FederatedException("The selected Identity Service is not supported by your client, please restart the process and choose an alternative provider")
        
## Get the list of all the IdP available
# @param keystoneEndpoint The keystone url
def getRealmList(keystoneEndpoint, v3):
#modify request by appending the endpoint with /auth/tokens
#build the body of the request. 
    data = {}
    if v3 == True:
        keystoneEndpoint += '/auth/tokens'
        data = {'auth': {
                   'identity': {
                       'methods': ['federated'],
                       'federated': {
                           'phase': 'discovery'
                        }
                    }
                }                                                      
                }

    #look at last param and understand the need for header with v2 and lack of header for v3.
    resp = futils.middlewareRequest(keystoneEndpoint, data, 'POST', not v3)
    info = json.loads(resp.data)
    return info

## Get the authentication request to send to the IdP
# @param keystoneEndpoint The keystone url
# @param realm The name of the IdP
def getIdPRequest(keystoneEndpoint, realm, v3):
    if v3 == True:
        keystoneEndpoint += '/auth/tokens'
        data = {'auth': {
                   'identity': {
                       'methods': ['federated'],
                       'federated': {
                           'phase': 'request',
                           'provider_id': realm['id']
                        }
                    }
                }                                                      
                }
    else:
        data = {'realm': realm}
    resp = futils.middlewareRequest(keystoneEndpoint, data, 'POST')            #Do we need a header for this request in v3?
    info = json.loads(resp.data)
    return info

## Get an unscoped token for the user along with the tenants list
# @param keystoneEndpoint The keystone url
# @param idpResponse The assertion retreived from the IdP
def getUnscopedToken(keystoneEndpoint, idpResponse, realm=None, v3=False):
    if realm is None:
        data = {'idpResponse' : idpResponse}
    else:
        if v3 == True:
            keystoneEndpoint += '/auth/tokens'
            data = {'auth': {
                   'identity': {
                       'methods': ['federated'],
                       'federated': {
                           'phase': 'validate',           #ok correct phase
                           'data': idpResponse,           #ok an assertion I think
                           'provider_id': realm['id']     #ok
                        }
                    }
                }                                                      
                } 
        else:
            data = {'idpResponse' : idpResponse, 'realm' : realm}
    resp = futils.middlewareRequest(keystoneEndpoint, data, 'POST', not v3)
    info = json.loads(resp.data)
    return info, resp

## Get a tenant-scoped token for the user
# @param keystoneEndpoint The keystone url
# @param idpResponse The assertion retreived from the IdP
# @param tenantFn The tenant friendly name
def getScopedToken(keystoneEndpoint, idpResponse, tenantFn):
    response = getUnscopedToken(keystoneEndpoint, idpResponse)
    type, tenantId = futils.getTenantId(response["tenants"])
    if tenantId is None:
        print "Error the tenant could not be found, should raise InvalidTenant"
    scoped = swapTokens(keystoneEndpoint, response["unscopedToken"], type, tenantId)
    return scoped

## Get a scoped token from an unscoped one
# @param keystoneEndpoint The keystone url
# @param unscopedToken The unscoped authentication token obtained from getUnscopedToken()
# @param tenanId The tenant Id the user wants to use
def swapTokens(keystoneEndpoint, unscopedToken, type, tenantId, v3):
    data = {'auth' : {'token' : {'id' : unscopedToken}, type : tenantId}}
    keystoneEndpoint+="/"
    if v3 == True:
       keystoneEndpoint+="auth/"
       data = {"auth": {"identity": {"methods": ["token"],"token": {"id": unscopedToken}, "scope":{}}}}
       if type == 'domainId':
           data["auth"]["identity"]["scope"]["domain"] = {"id": tenantId}
       else:
           data["auth"]["identity"]["scope"]["project"] = {"id": tenantId}
    resp = futils.middlewareRequest(keystoneEndpoint + "tokens", data,'POST', withheader = False)
    return json.loads(resp.data)
