import requests
import xml.etree.ElementTree as ET
from QBClientBase import QBClientBase
from QBCalendarItem import QBCalendarItem
import time


class QBCalendarClient(QBClientBase):

    auth_context = None
    auth_context = None

    def __init__(self, auth_context):
        super(QBClientBase, self).__init__()
        self.auth_context = auth_context


    def get_calendar_items(self, query):
        try:
            response=requests.get(query)
            response.raise_for_status()
            return self.process_query_response(response)
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return None

    def process_query_response(self, response):
        result = []
        xml = ET.fromstringlist(response.content)
        if not self.is_valid_response(xml):
            result = None
        else:
            for record in xml.iter('record'):
                item = QBCalendarItem()
                item.name = record.find("f[@id='18']").text
                item.record_id = record.find("f[@id='3']").text
                item.attending = record.find("f[@id='71']").text
                start_time = record.find("f[@id='77']").text
                if start_time is not None:
                    item.start_date = time.strptime(start_time, '%m-%d-%Y' )
                end_time = record.find("f[@id='80']").text
                if end_time is not None:
                    item.end_date = time.strptime(end_time, '%m-%d-%Y' )
                item.location = record.find("f[@id='19']").text
                item.url = record.find("f[@id='81']").text
                sponsors = record.find("f[@id='83']").text
                if sponsors is not None:
                    item.sponsors = sponsors.split(";")
                result.append(item)
        return result


