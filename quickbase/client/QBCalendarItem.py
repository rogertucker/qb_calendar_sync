class QBCalendarItem(object):

    def __init__(self, name='', record_id='', attending='', purpose='',
                 start_date='', end_date='', location='', url='', sponsors=[] ):
        self.name = name
        self.record_id = record_id
        self.attending = attending
        self.purpose = purpose
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.url = url
        self.sponsors = sponsors

