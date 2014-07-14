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

from keystoneclient.shell import OpenStackIdentityShell
from keystoneclient import exceptions
from keystoneclient.v2_0 import client
from keystoneclient import session
from keystoneclient.tests import utils


class FederatedAuthenticationTests(utils.TestCase):
    

    def setUp(self):
        super(FederatedAuthenticationTests, self).setUp()
        print('setting up federated tests...')
        # TEST_FEDERATED is True if the user has used the -F or --federated flag
        self.identity_shell=OpenStackIdentityShell()
        self.parser = self.identity_shell.get_base_parser()
        #self.add_federated_option()
        
    #Tests the command line parser for the use of the -F flag
    #If chosen by the client, the value of the parser.federated variable 
    #should be True and False otherwise. 

    def test_parser_federated_flag(self):
        options = self.parser.parse_args(['-F'])
        print('Options object: ',options)
        self.assertTrue(options.federated)

    #Tests the command line parser for the use of the --federated flag
    #If chosen by the clien, the the value of the parser.federated variable 
    #should be True and False otherwise. 

    def test_parser_F_flag(self):
        print('In test parser F')
        options = self.parser.parse_args(['--federated'])
        self.assertTrue(options.federated)

    #A test for behaviour in cases when user enters multiple federated flags
    def test_multiple_federated_flags(self):
        print('In test parser mutiple flags')
        options = self.parser.parse_args(['--federated', '-F'])
        self.assertTrue(options.federated)

    #Tests for federated False, when the flag is not used. We use a --version
    #flag to prevent the keystone client from throwing the no-args user message 
    #to the user. 
    def test_for_no_federated_flag(self):
        options = self.parser.parse_args(['--insecure'])
        self.assertFalse(options.federated)

    #for the purpose of this test, to see if it will succeed, we will
    #add another option to the parser to handle federation from within the 
    #test class. These patches will get rolled into the main source code when
    #I know they will not break the build!
    '''def add_federated_option(self):
        print('Creating new parser modification')
        self.parser.add_argument('--federated', '-F',
                            dest="federated", 
                            action='store_true',
                            help="This is the Federated Option")
    '''
