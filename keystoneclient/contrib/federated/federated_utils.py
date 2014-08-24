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

from keystoneclient import exceptions
import sys

#############
# The following functions are not part of the API
# They are tools to avoid code redundancy
#############


## Displays the list of tenants to the user so he can choose one
def selectTenantOrDomain(tenantsList, serverName=None):
    if not serverName:
        print('You have access to the following tenant(s)and domain(s):')
    else:
        print('You have access to the following tenant(s) and domain(s) on '
              + serverName + ':')
    for idx, tenant in enumerate(tenantsList):
        if tenant.get("project", None) is None and \
           tenant.get("domain", None) is None:
            print('\t{', idx, '} ', tenant['description'])
        else:
            if tenant.get("domain", None) is not None:
                print('\t{', idx, '} ', tenant['domain']['description'])
            else:
                print('\t{', idx, '} ', tenant['project']['description']
                      + ' @ ' + tenant["project"]["domain"]["name"])
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(tenantsList)) + ' }\tQuit')
    chosen = False
    choice = None
    while not chosen:
        try:
            choice = int(raw_input("Enter the number corresponding to " +
                                   "the tenant you want to use: "))
        except Exception:
            print('An error occurred with your selection')
        if choice is not None:
            if choice < 0 or choice > len(tenantsList):
                chosen = False
                print('The selection made was not a valid choice of tenant')
            else:
                chosen = True
    if choice == len(tenantsList):
        print('Quitting...')
        sys.exit(0)
    else:
        return tenantsList[choice]


## Displays the list of realm to the user
def selectRealm(realmList):
    print('Please use one of the following services to authenticate you:')
    if not realmList:
        raise exceptions.FederatedException('There are no available realms' +
                                            ' for the user specified')
    for idx, realm in enumerate(realmList):
        print('\t{ ' + str(idx) + ' }\t' + realm['id'])
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(realmList)) + ' }\tQuit')
    choice = None
    while choice is None:
        try:
            choice = int(raw_input('Enter the number corresponding ' +
                                   'to the service you want to use: '))
        except Exception:
            print('An error occurred with your selection')
        if choice < 0 or choice > len(realmList):
            print('The selection made was not a valid choice of service')
            choice = None
    if choice == len(realmList):
        print('Quitting...')
        sys.exit(0)
    else:
        return realmList[choice]


## Given a tenants list and a friendly name, returns the corresponding tenantId
#user gives a project name but specifies a name rather than ID, convert
def getTenantId(tenantsList, friendlyname):
    for idx, tenant in enumerate(tenantsList):
        if tenant.get("project", None) is not None:
            if tenant["project"]["name"] == friendlyname:
                return "tenantId", tenant["id"]


'''Allows the user to choose a protocol from
a list provided.
@param protocol_list the list of protocols returned by
the keystone server, for a specified IdP.
'''


def selectProtocol(protocol_list):
    print("Please choose one of the following protocols for authentication:")
    if not protocol_list:
        raise exceptions.FederatedException('There are no available ' +
                                            'protocols for the specified IdP')
    for index, realm in enumerate(protocol_list):
        print('\t{ ' + str(index) + ' }\t' + protocol_list[index]['id'])
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(protocol_list)) + ' }\tQuit')
    choice = None
    while choice is None:
        try:
            choice = int(raw_input('Enter the number corresponding ' +
                                   'to the protocol you want to use: '))
        except Exception:
            print('An error occurred with your selection')
        if choice < 0 or choice > len(protocol_list):
            print('The selection made was not a valid choice of service')
            choice = None
    if choice == len(protocol_list):
        print('Quitting...')
        sys.exit(0)
    else:
        return protocol_list[choice]


def select_project(item_list):
    print("Please choose one of the following Projects:")
    if not item_list:
        raise exceptions.FederatedException("There are no available projects.")
    for index, item in enumerate(item_list):
        print('\t{ ' + str(index) + ' }\t' + item_list[index]['name'])
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(item_list)) + ' }\tQuit')
    choice = None
    while choice is None:
        try:
            choice = int(raw_input('Enter the number corresponding' +
                                   ' to the project you want to use: '))
        except Exception:
            print('An error occurred with your selection')
        if choice < 0 or choice > len(item_list):
            print('The selection made was not a valid choice.')
            choice = None
    if choice == len(item_list):
        print('Quitting...')
        sys.exit(0)
    else:
        return item_list[choice]
