import json
import sys
import urllib
import urllib3
from keystoneclient import exceptions

#############
# The following functions are not part of the API
# They are tools to avoid code redundancy
#############

## Send a request that will be process by the Federation Middleware
# It add the X-Auth-Type: federated header in the HTTP request
def middlewareRequest(keystoneEndpoint, data={}, method="GET", withheader=True, pool=None):
    if withheader:
        headers = {'X-Authentication-Type': 'federated'}
    else:
	    headers = {}
    if pool is None:
        pool = urllib3.PoolManager()
    if method == "GET":
        data = urllib.urlencode(data)
        response = pool.request('GET', keystoneEndpoint, fields=data, headers=headers)
    elif method == "POST":
        data = json.dumps(data)
        headers['Content-Type'] = 'application/json'
        response = pool.urlopen('POST', keystoneEndpoint, body=data, headers=headers)
    return response

## Displays the list of tenants to the user so he can choose one
def selectTenantOrDomain(tenantsList, serverName=None):
    if not serverName:
        print('You have access to the following tenant(s)and domain(s):')
    else:
        print('You have access to the following tenant(s) and domain(s) on '
               + serverName + ':')
    for idx, tenant in enumerate(tenantsList):
        if tenant.get("project", None) is None and tenant.get("domain", None) is None:
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
            choice = int(raw_input("Enter the number corresponding to the tenant you want to use: "))
        except:
            print('An error occurred with your selection')
        if not choice is None:
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
    #print(realmList)
    print('Please use one of the following services to authenticate you:')
    if not realmList:
        raise exceptions.FederatedException('There are no available realms for the user specified')
    for idx, realm in enumerate(realmList):
        print('\t{ ' + str(idx) + ' }\t' + realm['name'])
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(realmList)) + ' }\tQuit')
    choice = None
    while choice is None:
    	try:
            choice = int(raw_input('Enter the number corresponding to the service you want to use: '))
    	except:
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
