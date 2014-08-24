'''
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

Icehouse Federation Benchmark Script v1.0 - BLM 2014
----------------------------------------------------------------
This benchmark is based on an Icehouse installation at
the University Of Kent. At time of writing, only a SAML
SSO IdP is available.

TO RUN THE BENCHMARK:
1. Make sure you have set the OS_IDENTITY_API_VERSION=3
via LINUX environment variables
2. Ensure you have set the AUTH_URL to the correct
endpoint.
3. Perform one complete authentication, leaving the browser
window open. This ensures SSO persistence via the browser
cookie.
----------------------------------------------------------------
'''


from keystoneclient.contrib.federated import federated
from keystoneclient.contrib.federated import federated_utils as futils
from keystoneclient.v3 import client
import time

TEST_RUNS = 1001
AUTH_URL = "http://icehouse.sec.cs.kent.ac.uk:5000/v3"
FILE_NAME = "benchmark_data.csv"


def patched_selectIdP(keystone_endpoint, identity_providers):
    """A patched version of the federated API that returns element 0
    from the list provided. The raw_input call has been removed.
    @param: keystone_endpoint. the authorisation url of the keystone
    server.
    @param: identity_providers. A list of IdPs returned by the Keystone
    server.
    """
    if not identity_providers:
        raise exceptions.FederatedException('There are no available ' +
                                            'IdPs at the os-auth-url' +
                                            ' specified')
    print('\nPlease choose a service to authenticate with:')
    auth_options = []
    index = 0
    print('\t' + ('-' * 38))
    print('\tIndex\t| IdP\t\t| Protocol\t')
    print('\t' + ('-' * 38))
    for IdP in identity_providers['identity_providers']:
        protocol_list = federated.get_protocol_List(keystone_endpoint, IdP)
        if not protocol_list:
            raise exceptions.FederatedException('There are no ' +
                                                'available protocols' +
                                                'for the specified IdP')
        for protocol in protocol_list['protocols']:
            print('\t{ ' + str(index) + ' }\t  ' + IdP['id'] +
                  '\t\t  ' + protocol['id'])
            auth_options.append({'IdP': IdP['id'],
                                 'protocol': protocol['id']})
            index += 1
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(auth_options)) + ' }\t  Quit')
    print('\t' + ('-' * 38))
    choice = 0
    if choice == len(auth_options):
        print('Quitting...')
        sys.exit(0)
    else:
        return auth_options[choice]


def patched_select_project(item_list):
    """A patched version of the federated API that returns element 0
    from the list provided. The raw_input call has been removed.
    @param: item_list. A list of projects returned by the keystone
    server, once the user has authenticated.
    """
    print("Please choose one of the following Projects:")
    if not item_list:
        raise exceptions.FederatedException("There are no available projects.")
    for index, item in enumerate(item_list):
        print('\t{ ' + str(index) + ' }\t' + item_list[index]['name'])
    #give the user a way to cancel with a quit option
    print('\t{ ' + str(len(item_list)) + ' }\tQuit')
    choice = 0
    if choice == len(item_list):
        print('Quitting...')
        sys.exit(0)
    else:
        return item_list[choice]


def create_monkey_patch():
    """Monkey-patches two functions in the federated library.
    This removes all user input from the program flow and
    always returns the first element in the IdP and project list.
    """
    federated.select_IdP_and_protocol = patched_selectIdP
    futils.select_project = patched_select_project
    print("Completed monkey-patching")


def create_log_file():
    """Creates a new log-file. Future file actions append the
    file created in this function.
    """
    log_file = open(FILE_NAME, 'w')
    log_file.write("Log-file created on " + time.strftime("%d/%m/%Y") +
                   " at " + time.strftime("%H:%M:%S") + "\n")
    log_file.close()


def run_benchmark():
    """The main benchmark function. Creates the patches, a log
    file and writes the duration of authentication to FILE_NAME
    """
    create_monkey_patch()
    create_log_file()
    start_time = None
    for x in range(0, TEST_RUNS):
        start_time = int(round(time.time() * 1000))
        print("Running itr:" + str(x))
        #create a v3 client for federated login.
        client.Client(auth_url=AUTH_URL, federated=True)
        end_time = int(round(time.time() * 1000))
        log_file = open(FILE_NAME, 'a')
        log_file.write(str(end_time - start_time) + ", ")
        log_file.close()

#entry point for the program
if __name__ == "__main__":
    run_benchmark()
