import xml.etree.ElementTree as ET
import requests
import os

class SPAuthContext:

    EXT_STS_URL = "https://login.microsoftonline.com/extSTS.srf"
    ACCESS_TOKEN_PATH = "_forms/default.aspx?wa=wsignin1.0"
    REQUEST_DIGEST_PATH = "_api/contextinfo"
    EXT_STS_USERNAME_TOKEN_PATH = "s:Header/o:Security/o:UsernameToken"
    EXT_STS_ENDPOINT_PATH = "s:Body/t:RequestSecurityToken/wsp:AppliesTo/a:EndpointReference/a:Address"
    FORM_DIGEST_PATH = "d:FormDigestValue"
    EXT_STS_USERNAME_ELEMENT = "o:Username"
    EXT_STS_PASSWORD_ELEMENT = "o:Password"
    EXT_STS_REQUEST_NS = {
        "s":"http://www.w3.org/2003/05/soap-envelope",
        "o":"http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
        "t":"http://schemas.xmlsoap.org/ws/2005/02/trust",
        "wsp":"http://schemas.xmlsoap.org/ws/2004/09/policy",
        "a":"http://www.w3.org/2005/08/addressing"
    }

    EXT_STS_RESPONSE_NS = {
        "S":"http://www.w3.org/2003/05/soap-envelope",
        "wsse":"http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
        "wsu":"http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd",
        "wsa":"http://www.w3.org/2005/08/addressing",
        "wst":"http://schemas.xmlsoap.org/ws/2005/02/trust",
        "psf":"http://schemas.microsoft.com/Passport/SoapServices/SOAPFault"
    }

    REQUEST_DIGEST_RESPONSE_NS = {
        "d":"http://schemas.microsoft.com/ado/2007/08/dataservices"
    }

    BINARY_SECURITY_TOKEN_PATH = "S:Body/wst:RequestSecurityTokenResponse/wst:RequestedSecurityToken/wsse:BinarySecurityToken"

    def __init__(self, sp_url, username, password):
        self.sp_url = sp_url
        self.username = username
        self.password = password

    def authenticate(self):
        if self.get_security_token() and self.get_access_cookies() and self.get_form_digest_value():
            return True
        else:
            return False


    def get_security_token(self):
        result = True
        extSTS = ET.ElementTree()
        extSTS.parse("{}/saml.xml".format(os.path.join(os.path.dirname(__file__))))
        root = extSTS.getroot()
        username_token = root.find(self.EXT_STS_USERNAME_TOKEN_PATH, self.EXT_STS_REQUEST_NS)
        username = username_token.find(self.EXT_STS_USERNAME_ELEMENT, self.EXT_STS_REQUEST_NS)
        username.text = self.username
        password = username_token.find(self.EXT_STS_PASSWORD_ELEMENT, self.EXT_STS_REQUEST_NS )
        password.text = self.password
        endpoint = root.find(self.EXT_STS_ENDPOINT_PATH, self.EXT_STS_REQUEST_NS)
        endpoint.text = self.sp_url
        try:
            response = requests.post(self.EXT_STS_URL, ET.tostring(root, "utf-8", "xml"))
            response.raise_for_status()
            binary_security_token = self.process_service_token_response(response.content)
            if(binary_security_token):
                self.binary_security_token = binary_security_token
            else:
                result = False
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            result =  False

        return result

    def process_service_token_response(self, response):
        result = None
        xml = ET.fromstring(response)

        #check for errors
        if xml.find('S:Body/S:Fault', self.EXT_STS_RESPONSE_NS) is not None :
            error = xml.find('S:Body/S:Fault/S:Detail/psf:error/psf:internalerror/psf:text', self.EXT_STS_RESPONSE_NS)
            self.error ='An error occured while retrieving token: {0}'.format(error.text)

        else:
            binary_security_token = xml.find(self.BINARY_SECURITY_TOKEN_PATH, self.EXT_STS_RESPONSE_NS)
            if (binary_security_token != None):
                result = binary_security_token.text
        return result

    def get_access_cookies(self):
        result = True
        try:
            response = requests.post(self.sp_url + self.ACCESS_TOKEN_PATH, self.binary_security_token)
            response.raise_for_status()
            if 'FedAuth' in response.cookies and 'rtFa' in response.cookies:
                self.access_token_cookies = requests.utils.dict_from_cookiejar(response.cookies)
            else:
                self.error = "An error occured while retrieving auth cookies"
                result = False

        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            result =  False

        return result

    def get_form_digest_value(self):
        result = True
        try:
            response = requests.post(self.sp_url + self.REQUEST_DIGEST_PATH, cookies=self.access_token_cookies)
            response.raise_for_status()
            self.process_form_digest_response(response)
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            result =  False

        return result

    def process_form_digest_response(self, response):
        xml = ET.fromstring(response.content)
        form_digest_value = xml.find(self.FORM_DIGEST_PATH, self.REQUEST_DIGEST_RESPONSE_NS)
        if form_digest_value != None:
            self.form_digest_value = form_digest_value.text
