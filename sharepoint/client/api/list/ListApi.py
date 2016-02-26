import requests
import json

class ListApi:

    def __init__(self, auth_context):
        self.auth_context = auth_context

    def get_lists(self, site="", accept="xml"):
        url = self.get_api_base(site) + "lists"
        return self.get(url, accept)

    def get_list_by_title(self, site="", title="", accept="xml"):
        url = self.get_api_base(site) + "lists/getByTitle('{0}')".format(title)
        response = self.get(url, accept)
        return self.handle_response(response)

    def get_list_items_by_title(self, site="", title="", accept="xml"):
        url = self.get_api_base(site) + "lists/getByTitle('{0}')/items".format(title)
        response = self.get(url, accept);
        return self.handle_response(response)

    def add_list_item(self, site, title, item, accept="xml"):
        url = self.get_api_base(site) + "lists/getByTitle('{0}')/items".format(title)
        body = item.item_to_json();
        headers = {}
        headers["content-type"] = "application/json;odata=verbose"
        headers["content-length"] = len(body)
        response = self.post(url, accept, headers, body)
        return self.handle_response(response)

    def update_list_item(self, site, title, item_id, item, accept="xml"):
        url = self.get_api_base(site) + "lists/getByTitle('{0}')/items({1})".format(title, item_id)
        body = item.item_to_json();
        headers = {}
        headers["content-type"] = "application/json;odata=verbose"
        headers["content-length"] = len(body)
        headers["IF-MATCH"] = "*"
        headers["X-HTTP-Method"] = "MERGE"
        response = self.post(url, accept, headers, body)
        return self.handle_response(response)

    def delete_list_item(self, site, title, item_id, accept="xml"):
        url = self.get_api_base(site) + "lists/getByTitle('{0}')/items({1})".format(title, item_id)
        headers={}
        headers["IF-MATCH"] = "*"
        headers["X-HTTP-Method"] = "DELETE"
        response = self.post(url, accept, headers)
        return self.handle_response(response)


    def get(self, url, accept, headers={}):
        self.add_auth_headers(headers)
        self.add_accept_header(accept, headers)
        response=requests.get(url, headers=headers, cookies=self.auth_context.access_token_cookies)
        return response

    def post(self, url, accept, headers={}, body=""):
        self.add_auth_headers(headers)
        self.add_accept_header(accept, headers)
        print "headers=%s"%headers
        print "cookies=%s"%self.auth_context.access_token_cookies
        response=requests.post(url, headers=headers, cookies=self.auth_context.access_token_cookies, data=body)
        return response


    def get_api_base(self, site):
        return self.auth_context.sp_url + site + "_api/web/"

    def add_auth_headers(self, headers={}):
        return self.add_header("X-RequestDigest", self.auth_context.form_digest_value, headers)

    def add_accept_header(self, accept, headers={}):
        value = "application/"+accept+";odata=verbose"
        return self.add_header("accept", value, headers)

    def add_header(self, key, value, headers):
        headers[key] = value
        return headers

    def handle_response(self, response):
        try:
            response.raise_for_status()
            if response._content:
                return json.loads(response.content)
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)












