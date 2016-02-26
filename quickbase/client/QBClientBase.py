class QBClientBase(object):

    def __init__(self):
        self.error = ''

    def is_valid_response(self, xml):
        result = True
        errcode = xml.find("errcode")
        if errcode == None:
            self.error = "The repsonse was invalid"
            result = False
        elif errcode.text <> '0':
            errtext = xml.find("errtext")
            self.error = "The authentication response returned an error: Error: {}".format(errtext.text)
            result = False
        return result