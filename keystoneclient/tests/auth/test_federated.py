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

# This module tests for federated functionality

#from keystoneclient.v2_0 import client
#from keystoneclient import exceptions
from keystoneclient.shell import OpenStackIdentityShell
#from keystoneclient import session
from keystoneclient.tests import utils

#NOTE: the print statements will only show when tox debug is invoked
#in all other cases print statements to stdout seem to be suppressed.  
class FederatedAuthenticationTests(utils.TestCase):
    
    #setUp is called for each test function, hence we don't have to
    #worry about persistent changes made to any test objects mutated
    #between test functions.
    def setUp(self):
        super(FederatedAuthenticationTests, self).setUp()
        print('Setting up federated tests...')
        # TEST_FEDERATED. True if user has used the -F or --federated flag
        self.identity_shell = OpenStackIdentityShell()
        self.parser = self.identity_shell.get_base_parser()

    #Tests the command line parser for the use of the -F flag
    #If chosen by the user, the value of the parser.federated variable
    #should be True and False otherwise.

    def test_parser_federated_flag(self):
        options = self.parser.parse_args(['-F'])
        print('Testing parser for the single -F flag')
        self.assertTrue(options.federated)

    #Tests the command line parser for the use of the --federated flag
    #If chosen by the user, the the value of the parser.federated variable
    #should be True and False otherwise.

    def test_parser_F_flag(self):
        print('Testing parser for single --federated flag')
        options = self.parser.parse_args(['--federated'])
        self.assertTrue(options.federated)

    #A test for behaviour in cases when user mistakenly enters 
    #multiple federated flags.
    def test_multiple_federated_flags(self):
        print('Testing parser for handling mutiple flags')
        options = self.parser.parse_args(['--federated', '-F'])
        self.assertTrue(options.federated)

    '''Tests for federated False, when the flag is not used. We use 
    a --insecure flag to prevent the keystone client from throwing 
    the no-args user message to the user. Note that --insecure is a 
    flag the requires no arguments. There is an issue regarding any 
    command that prints to stdout. The act of printing will halt 
    remaining tests and report test success. 
    NOTE: If having problems with your tests, check there is no output 
    being printed.'''
    def test_for_no_federated_flag(self):
        options = self.parser.parse_args(['--insecure'])
        self.assertFalse(options.federated)

    '''
    #tests for the correct parameter being passed to the HTTPClient object
    #test succeeds if user chooses federation and the HTTPClient.federation
    #is equal to True.
    def test_HTTPClient_fields(self):
        options = self.parser.parse_args(['-F', '--os-auth-url', 'http://foobarr.com'])
        api_version = options.os_identity_api_version
        self.cs = self.identity_shell.get_api_class(api_version)(
        federated=options.federated)
        self.assertTrue(self.identity_shell.cs.federated) 

    #tests for a missing --os-auth-url parameter when user chooses federated
    #authentication. Builds a fake command and processes accordingly. The test
    #succeeds if a CommandError is raised.
    def test_missing_auth_url(self):
        argv = ['-F', '--os-auth-url', 'http://foo-bar.com']
        print('Testing parser for the omission of --os-auth-url')
        options = self.parser.parse_args(argv)

        #determine correct arguments before checking correct combinations
        api_version = options.os_identity_api_version
        subcommand_parser = self.identity_shell.get_subcommand_parser(api_version)
        args = subcommand_parser.parse_args(argv)
        
        self.assertRaises(CommandError, self.identity_shell.auth_check(args))
    '''
