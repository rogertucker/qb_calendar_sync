import requests
import xml.etree.ElementTree as ET
from QBClientBase import QBClientBase


class QBAuthContext(QBClientBase):

    def __init__(self, url, username, password, hours=24):
        super(QBClientBase, self).__init__()
        self.url = url;
        self.username = username;
        self.password = password;
        self.hours = hours
        self.ticket = None


    def authenticate(self):
        url = "{0}/db/main?a=API_Authenticate&username={1}&password={2}&hours={3}".format(self.url, self.username, self.password, self.hours)
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.process_api_authenticate(response)

        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def process_api_authenticate(self, response):
        result = True
        xml = ET.fromstring(response.content)
        #Handle any errors
        if not self.is_valid_response(xml):
            result = False
        else:
            self.ticket = xml.find("ticket").text
        return result







