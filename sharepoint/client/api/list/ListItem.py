import json
from util.DateEncoder import DateEncoder
class ListItem:

    body={}

    def __init__(self, list_item_entity_type_full_name):
        self.body["__metadata"]={"type": list_item_entity_type_full_name}

    def add(self, key, value):
        self.body[key] = value
        return self

    def item_to_json(self):
        return json.dumps(self.body, cls=DateEncoder)