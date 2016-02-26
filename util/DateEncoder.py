import json
import time
from time import mktime
from datetime import datetime
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time.struct_time):
            dt = datetime.fromtimestamp(mktime(obj))
            print dt.isoformat()
            return dt.isoformat()
        return json.JSONEncoder.default(self, obj)
