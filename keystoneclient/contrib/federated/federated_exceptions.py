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

'''
This modeule is marked for deprecation and should
not be used any longer within any new client implementation.
See the general exceptions class for the client and
define the Federated exceptions there.
'''


class UnknownRealm(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class UnableToConnect(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class InvalidTenantID(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class CommunicationsError(Exception):
    pass


class SyntaxError(Exception):
    pass


class InvalidIdpMessage(Exception):
    pass
