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

# This module tests the keystoneClient for its federated functionality
# Additional tests are made to the federated API. These tests currently
# succeed for Keystone v2(grizzly) and v3(Savannah).

'''NOTE:print statements only show when 'tox debug' is invoked in all
other cases print statements to stdout seem to be suppressed. If you
must display a message for testing/debug then print to sys.stderr.write()'''

import sys
import types

from keystoneclient.v2_0 import client
from keystoneclient import exceptions
from keystoneclient.shell import OpenStackIdentityShell
from keystoneclient import session
from keystoneclient.v2_0 import shell as shell_v2_0
from keystoneclient.tests import utils

from keystoneclient.contrib.federated import federated as federated_API
from keystoneclient.contrib.federated import federated_utils as federated_API_utils

'''NOTE: print statements to stdout are likely to break the
testing harness, halting all tests at the print call and returning
success. If you are having problems getting all tests to run, try
removing print statements. '''

class FederatedAuthenticationTests(utils.TestCase):


    '''setUp is called for each test function, hence we don't have to
    worry about persistent changes made to any test objects mutated
    between test functions.
    '''
    def setUp(self):
        super(FederatedAuthenticationTests, self).setUp()
        '''crates an OpenStackIdentityShell object to parse arguments.'''
        self.identity_shell = OpenStackIdentityShell()
        self.parser = self.identity_shell.get_base_parser()
        self.REALM_LIST = [{u'description': u'Moonshot', u'type': u'idp.moonshot', u'id': u'590b18a65c2e44e6817ba70280c04c33', u'links': {u'self': u'http://localhost:5000/v3/services/590b18a65c2e44e6817ba70280c04c33'}, u'name': u'Moonshot'}, {u'description': u'Kent Keystone Identity Server', u'type': u'idp.keystonev2', u'id': u'9aa3246a42dd4f448f7da8fa256bae16', u'links': {u'self': u'http://localhost:5000/v3/services/9aa3246a42dd4f448f7da8fa256bae16'}, u'name': u'Kent Keystone Identity Server'}, {u'description': u'Kent Proxy Identity Service', u'type': u'idp.saml', u'id': u'fade8296c412408cba329505e464acd3', u'links': {u'self': u'http://localhost:5000/v3/services/fade8296c412408cba329505e464acd3'}, u'name': u'Kent Proxy Identity Service'}]

    '''Tests the command line parser for the use of the -F flag
    Test succeeds when the -F flag sets options.federated
    to true.
    '''
    def test_parser_federated_flag(self):
        options = self.parser.parse_args(['-F'])
        self.assertTrue(options.federated)

    '''Tests the command line parser for the --federated flag
    Test succeeds when the --federated flag sets options.federated
    to true.
    '''
    def test_parser_F_flag(self):
        options = self.parser.parse_args(['--federated'])
        self.assertTrue(options.federated)

    '''Test for adverse behaviour when user mistakenly enters
    multiple federated flags.
    Test succeeds by ignoring duplication and assigning True to the
    parser object.
    '''
    def test_multiple_federated_flags(self):
        options = self.parser.parse_args(['--federated', '-F'])
        self.assertTrue(options.federated)

    '''Tests the client for a missing --os-auth-url
    Test succeeds when a missing os_auth_url raises a CommandError
    exception.
    '''
    def test_missing_auth_url(self):
        args = self.parser.parse_args(['-F'])
        self.assertRaises(exceptions.CommandError,
                          self.identity_shell.auth_check,
                          args)

    '''Tests the keystone client for 'normal' behaviour w/ no federation
    Test succeeds when options.federated is False.
    '''
    def test_for_no_federated_flag(self):
        options = self.parser.parse_args(['--insecure'])
        self.assertFalse(options.federated)

    '''Tests the federated API for a a blank realm list.
    Test succeeds when a FederatedException is raised as a result of an
    empty realm list.
    '''
    def test_empty_realm_list(self):
        self.assertRaises(exceptions.FederatedException,
                          federated_API_utils.selectRealm,
                          None)

    '''Tests the API for use of a correct protocol module.
    Test succeeds when a correct python module is loaded.
    '''
    def test_load_module(self):
        loaded_module = federated_API.load_protocol_module('saml')
        self.assertTrue(isinstance(loaded_module, types.ModuleType))

    '''Tests the API for naming a non-existant or incorrect protocol module.
    Test succeeds when a FederatedException is raised.
    '''
    def test_bad_module(self):
        #loaded_module = federated.load_protocol_module('ben')
        self.assertRaises(exceptions.FederatedException,  
                          federated_API.load_protocol_module,
                          'ben')
        #self.assertFalse(isinstance(loaded_module, types.ModuleType))

    
#create a for loop and loop in values from a list to test for spurious input.

    
    
    def bad_realm_choice(self, realmList):
        print('Please use one of the following services to authenticate you:')
        if not realmList:
	    raise exceptions.FederatedException('There are no available realms for the user specified')
        for idx, realm in enumerate(realmList):
	    print('\t{ ' + str(idx) + ' }\t' + realm['name'])
        #give the user a way to cancel with a quit option
        print('\t{ ' + str(len(realmList)) + ' }\tQuit')
        choice = 'qwe'
    	try:
	    choice = int(choice)
    	except:
            raise exceptions.FederatedException('Invalid choice from realm list.')
	    print('An error occurred with your selection')
	if choice < 0 or choice > len(realmList):
	    print('The selection made was not a valid choice of service')
	    choice = None
        if choice == len(realmList):
	    print('Quitting...')
	    sys.exit(0)
        else:
	    return realmList[choice]

    def test_bad_realm_choice(self):
        #patch the function
        federated_API_utils.selectRealm = self.bad_realm_choice
        self.assertRaises(exceptions.FederatedException,
                          federated_API_utils.selectRealm, 
                          self.REALM_LIST)

