from  quickbase.client.QBAuthContext import QBAuthContext
from  quickbase.client.QBCalendarClient import QBCalendarClient
from sharepoint.client.auth.SPAuthContext import SPAuthContext
from sharepoint.client.api.list.ListApi import ListApi
from sharepoint.client.api.list.ListItem import ListItem
import settings



def qb_authenticate():
    qb_auth = QBAuthContext(settings.QB_DOMAIN, settings.QB_USERNAME, settings.QB_PASSWORD)
    if qb_auth.authenticate():
        return qb_auth

def sp_authenticate():
    sp_auth = SPAuthContext(settings.SP_DOMAIN, settings.SP_USERNAME, settings.SP_PASSWORD)
    if not sp_auth.authenticate():
        print "The sharepoint authentication failed.  " + sp_auth.error
    else:
        return sp_auth

def sync_calendars(qb_client, sp_list_api, list_item_entity_type_full_name, qb_query):

    cal_items = qb_client.get_calendar_items(qb_query)
    if cal_items is None:
        print "There was an error retrieving the calendar items.  " + qb_client.error
        return

    response = sp_list_api.get_list_items_by_title("People/ConsultantTraining/", "Test_DP_Calendar", "json")
    if "Error" in response:
       print response
       return
    else:
       sp_items = response["d"]["results"]

    for cal_item in cal_items:
        sp_filter = filter(lambda record: record['RecordId'] == cal_item.record_id, sp_items)
        list_item = build_list_item(cal_item, list_item_entity_type_full_name)
        if len(sp_filter) > 0:
            response = sp_list_api.update_list_item("People/ConsultantTraining/", "Test_DP_Calendar", sp_filter[0]["ID"], list_item, "json")
        else:
            response = sp_list_api.add_list_item("People/ConsultantTraining/", "Test_DP_Calendar", list_item, "json")
        if response and "Error" in response:
            print response

    for sp_item in sp_items:
        if sp_item["RecordId"]:
            cal_filter = filter(lambda record: record.record_id == sp_item["RecordId"], cal_items)
            if len(cal_filter) == 0:
                response = sp_list_api.delete_list_item("People/ConsultantTraining/", "Test_DP_Calendar", sp_item["ID"], "json")
            if response and "Error" in response:
                print response

def build_list_item(cal_item, list_item_entity_type_full_name):
    list_item = ListItem(list_item_entity_type_full_name);
    list_item.add("RecordId", cal_item.record_id)
    list_item.add("Title", cal_item.name)
    list_item.add("Location", cal_item.location)
    list_item.add("EndDate", cal_item.end_date)
    list_item.add("Category", cal_item.purpose)
    list_item.add("EventDate", cal_item.start_date)
    list_item.add("RecordURL", cal_item.url)
    list_item.add("PSC_x0020_Sponsor", ', '.join(cal_item.sponsors))
    return list_item


qb_client = None
sp_list_api = None
qb_auth = qb_authenticate()
if(qb_auth):
    qb_client = QBCalendarClient(qb_auth)
else:
    print "The Quickbase authentication failed.  " + qb_auth.error


sp_auth = sp_authenticate()
if(sp_auth):
    sp_list_api = ListApi(sp_auth)
else:
    exit(0)

response = sp_list_api.get_list_by_title("People/ConsultantTraining/", "Test_DP_Calendar", "json")
list_item_entity_type_full_name = None
if "Error" in response:
    print response
else:
    list_item_entity_type_full_name = response["d"]["ListItemEntityTypeFullName"]

qb_query = "{0}/db/bjrtmeegz?a=API_DoQuery&includeRids=1" \
          "&ticket={1}&apptoken=bup4z3abs83ububhkxc27j7ntvp&udata=mydata" \
          "&query={{'18'.XSW.'z'}}&clist=18.3.71.6.74.77.80.19.81.83" \
          "&slist=18&options=sortorder-A&fmt=structured".format(qb_auth.url, qb_auth.ticket)

sync_calendars(qb_client, sp_list_api, list_item_entity_type_full_name, qb_query)

















