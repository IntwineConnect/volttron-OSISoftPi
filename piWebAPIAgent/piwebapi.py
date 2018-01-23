########################################################################
# Copyright (c) 2017, Intwine Connect, LLC.                            #
# This file is licensed under the BSD-3-Clause                         #
# See LICENSE for complete text                                        #
########################################################################

import datetime
import urllib2
import json
import base64
import dateutil.parser


class PIWebAPI:
    server = ''
    auth = ''
    points = dict()

    def __init__(self, server, auth):
        self.server = server
        authkey = "Basic " + str(base64.b64encode('%s:%s' % auth))
        self.auth = {"Authorization": authkey}

    def validate_connection(self):
        request = urllib2.Request(self.server, headers=self.auth)
        result = urllib2.urlopen(request)

        return result.getcode() == 200

    def monitor_point(self, name, webId):
        self.points[name] = PIWebAPIPoint(webId, self.server, self.auth, name=name)
        self.points[name].read_latest_value()
        #print self.points[name].get_value()
        return self.points[name]

    def get_data(self):
        request = urllib2.Request(self.server, headers=self.auth)
        result = urllib2.urlopen(request)
        response = ""
        for line in result:
            response += line
        result.close()

        return json.loads(response)

class PIWebAPIPoint:
    webId = ''
    units = ''
    name = ''
    readable_name = None
    timestamp = datetime.datetime.utcfromtimestamp(0)
    value = None
    server = ''
    auth = ''
    path = ''
    descriptor = ''

    def __init__(self, webId, server, auth, name=None):
        self.webId = webId
        self.server = server
        self.auth = auth
        self.readable_name = name
        self.getPointInformation()

    def getPointInformation(self):
        # do the /point/{WebId} API call
        uri = self.server + "//points//" + self.webId
        request = urllib2.Request(uri, headers=self.auth)
        result = urllib2.urlopen(request)
        response = ""
        for line in result:
            response += line
        result.close()
        response = json.loads(response)

        self.units = response['EngineeringUnits']
        self.path = response['Path']
        self.name = response['Name']
        self.descriptor = response['Descriptor']

        if self.readable_name is None:
            self.readable_name = self.name
        
        return True

    def readValue(self):
        # update value /streams/{WebId}/value
        uri = self.server + "//streams//" + self.webId + "//value"
        request = urllib2.Request(uri, headers=self.auth)
        result = urllib2.urlopen(request)

        if result.getcode() != 200:
            return None

        response = ""
        for line in result:
            response += line
        result.close()
        response = json.loads(response)

        ts = dateutil.parser.parse(response['Timestamp']).replace(tzinfo=None)
        v = response['Value']
        good = response['Good']

        return ts, v, good

    def update_if_value_new(self, value):
        if value[2]:
            if value[0] > self.timestamp:
                self.value = value[1]
                self.timestamp = value[0]
                return True

    def read_latest_value(self):
        res = self.readValue()
        return self.update_if_value_new(res)

    def get_value(self):
        return self.timestamp, self.value, self.units

    def get_serializable(self):
        ts, v, u = self.get_value()
        rsp = {'timestamp': datetime.datetime.isoformat(ts, 'Z'),
               'value': v,
               'units': u}
        return rsp
