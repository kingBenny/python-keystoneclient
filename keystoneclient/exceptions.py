# Copyright 2010 Jacob Kaplan-Moss
# Copyright 2011 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""
Exception definitions.
"""

#flake8: noqa
from keystoneclient.openstack.common.apiclient.exceptions import *

# NOTE(akurilin): This alias should be left here to support backwards
# compatibility until we are sure that usage of these exceptions in
# projects is correct.
ConnectionError = ConnectionRefused
HTTPNotImplemented = HttpNotImplemented
Timeout = RequestTimeout
HTTPError = HttpError


class CertificateConfigError(Exception):
    """Error reading the certificate"""
    def __init__(self, output):
        self.output = output
        msg = ("Unable to load certificate. "
               "Ensure your system is configured properly.")
        super(CertificateConfigError, self).__init__(msg)


class CMSError(Exception):
    """Error reading the certificate"""
    def __init__(self, output):
        self.output = output
        msg = ("Unable to sign or verify data.")
        super(CMSError, self).__init__(msg)


class EmptyCatalog(EndpointNotFound):
    """The service catalog is empty."""
    pass


class SSLError(ConnectionRefused):
    """An SSL error occurred."""


class DiscoveryFailure(ClientException):
    """Discovery of client versions failed."""


class VersionNotAvailable(DiscoveryFailure):
    """Discovery failed as the version you requested is not available."""


class MethodNotImplemented(ClientException):
    """Method not implemented by the keystoneclient API."""


class MissingAuthPlugin(ClientException):
    """An authenticated request is required but no plugin available."""


class NoMatchingPlugin(ClientException):
    """There were no auth plugins that could be created from the parameters
    provided."""


class InvalidResponse(ClientException):
    """The response from the server is not valid for this request."""

    def __init__(self, response):
        super(InvalidResponse, self).__init__()
        self.response = response

class FederatedException(ClientException):

    def __init__(self, msg, http_scheme='', http_host='', http_port='',
                 http_path='', http_query='', http_status=0, http_reason='',
                 http_device='', http_response_content=''):
        Exception.__init__(self, msg)
        self.msg = msg
        self.http_scheme = http_scheme
        self.http_host = http_host
        self.http_port = http_port
        self.http_path = http_path
        self.http_query = http_query
        self.http_status = http_status
        self.http_reason = http_reason
        self.http_device = http_device
        self.http_response_content = http_response_content

    def __str__(self):
        a = self.msg
        b = ''
        if self.http_scheme:
            b += '%s://' % self.http_scheme
        if self.http_host:
            b += self.http_host
        if self.http_port:
            b += ':%s' % self.http_port
        if self.http_path:
            b += self.http_path
        if self.http_query:
            b += '?%s' % self.http_query
        if self.http_status:
            if b:
                b = '%s %s' % (b, self.http_status)
            else:
                b = str(self.http_status)
        if self.http_reason:
            if b:
                b = '%s %s' % (b, self.http_reason)
            else:
                b = '- %s' % self.http_reason
        if self.http_device:
            if b:
                b = '%s: device %s' % (b, self.http_device)
            else:
                b = 'device %s' % self.http_device
        if self.http_response_content:
            if len(self.http_response_content) <= 60:
                b += '   %s' % self.http_response_content
            else:
                b += '  [first 60 chars of response] %s' \
                    % self.http_response_content[:60]
        return b and '%s: %s' % (a, b) or a
