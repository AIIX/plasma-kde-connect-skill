import sys
import os
import dbus
import xmltodict
import httplib2
import base64
from traceback import print_exc
from os.path import dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
from apiclient.discovery import build
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow

__author__ = 'aix'

LOGGER = getLogger(__name__)
global contactNumber


class KDEConnectSkill(MycroftSkill):

    def __init__(self):
        super(KDEConnectSkill, self).__init__(name="KDEConnectSkill")
    
    @intent_handler(IntentBuilder("FindMyPhone").require("FindMyPhoneKeyword").build())
    def handle_findmyphone_intent(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.kdeconnect", "/modules/kdeconnect/devices")
        getNode = remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
        xmldoc = xmltodict.parse(getNode)
        try:
            for i in range(len(xmldoc['node']['node'])):
                nodeName = xmldoc['node']['node'][i]['@name']
                findNodeObject = "/modules/kdeconnect/devices/{0}".format(nodeName)
                sub_object = bus.get_object("org.kde.kdeconnect", findNodeObject)
                sub_result = sub_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
                nodedoc = xmltodict.parse(sub_result)
                if 'node' in nodedoc['node'].keys():
                    nodeName = findNodeObject
        except:
                singleNode = xmldoc['node']['node']['@name']
                nodeName = "/modules/kdeconnect/devices/{0}".format(singleNode)
        findPhoneNodePath = "{0}/findmyphone".format(nodeName)
        remote_object2 = bus.get_object("org.kde.kdeconnect", findPhoneNodePath)
        remote_object2.ring(dbus_interface="org.kde.kdeconnect.device.findmyphone")
        self.speak("Calling your device!")

    @intent_handler(IntentBuilder("PingMyPhone").require("PingMyPhoneKeyword").build())
    def handle_pingmyphone_intent(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.kdeconnect", "/modules/kdeconnect/devices")
        getNode = remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
        xmldoc = xmltodict.parse(getNode)
        try:
            for i in range(len(xmldoc['node']['node'])):
                nodeName = xmldoc['node']['node'][i]['@name']
                findNodeObject = "/modules/kdeconnect/devices/{0}".format(nodeName)
                sub_object = bus.get_object("org.kde.kdeconnect", findNodeObject)
                sub_result = sub_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
                nodedoc = xmltodict.parse(sub_result)
                if 'node' in nodedoc['node'].keys():
                    nodeName = findNodeObject
        except:
                singleNode = xmldoc['node']['node']['@name']
                nodeName = "/modules/kdeconnect/devices/{0}".format(singleNode)
        pingPhoneNodePath = "{0}/ping".format(nodeName)
        remote_object2 = bus.get_object("org.kde.kdeconnect", pingPhoneNodePath)
        remote_object2.sendPing("Ping From Mycroft!", dbus_interface="org.kde.kdeconnect.device.ping")
    
    @intent_handler(IntentBuilder("ShowMyPhoneFiles").require("ShowMyPhoneFilesKeyword").build())
    def handle_showmyphonefiles_intent(self, message):
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.kdeconnect", "/modules/kdeconnect/devices")
        getNode = remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
        xmldoc = xmltodict.parse(getNode)
        try:
            for i in range(len(xmldoc['node']['node'])):
                nodeName = xmldoc['node']['node'][i]['@name']
                findNodeObject = "/modules/kdeconnect/devices/{0}".format(nodeName)
                sub_object = bus.get_object("org.kde.kdeconnect", findNodeObject)
                sub_result = sub_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
                nodedoc = xmltodict.parse(sub_result)
                if 'node' in nodedoc['node'].keys():
                    nodeName = findNodeObject
        except:
                singleNode = xmldoc['node']['node']['@name']
                nodeName = "/modules/kdeconnect/devices/{0}".format(singleNode)
        sftpPhoneNodePath = "{0}/sftp".format(nodeName)
        remote_object2 = bus.get_object("org.kde.kdeconnect", sftpPhoneNodePath)
        remote_object2.startBrowsing(dbus_interface="org.kde.kdeconnect.device.sftp")
        self.speak("Displaying files from the device")
        
    @intent_handler(IntentBuilder("SendSMSKeywordIntent").require("SendSMSPlasmaDesktopSkillKeyword").build())
    def handle_sendsms_plasma_desktopskill_intent(self, message):
        utterance = message.data.get('utterance')
        utteranceChanged = utterance.replace(message.data.get("SendSMSPlasmaDesktopSkillKeyword"), '')
        nameString = utteranceChanged.lstrip()

        cid_en = "NTQ3MDI1NTQ3OTM2LXNhZG83cDRxNjhkZTJwNnE2cmUxaXZlZmFpODkwY3U2LmFwcHMuZ29vZ2xldXNlcmNvbnRlbnQuY29t"
        cis_en = "c2tLN0c4WnhRWmRpMHM1OV94Q28ybTdl"
        scope = 'https://www.googleapis.com/auth/contacts.readonly'
        cid = base64.b64decode(cid_en)
        cis = base64.b64decode(cis_en)
        flow = OAuth2WebServerFlow(cid, cis, scope)
        
        #Setup Credential Flow
        storage = Storage('credentials.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build('people', 'v1', http=http)
        
        #Call People API for Contacts
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=1000,
            requestMask_includeField='person.names,person.phoneNumbers')
        res = results.execute()
        connections = res.get('connections', [])
        contactPhone = self.extractPhoneNumber(nameString, connections)
        global contactNumber 
        contactNumber = contactPhone
        self.speak("What message would you like to send ?", expect_response=True)
    
    #Extract Contact Information From Matched Name
    def extractPhoneNumber(self, name, connections):
        for person in connections:
            names = person.get('names' ,[])
            if len(names) > 0 and names[0].get('displayName').lower().replace(' ', '') == name.lower().replace(' ', ''):
                phone_numbers = person.get('phoneNumbers',[])
                if len(phone_numbers) > 0:
                    return phone_numbers[0].get('value')
                
    @intent_handler(IntentBuilder("SendSmsGetContentIntent").require("SendSmsGetContentKeyword").build())
    def handle_sendsms_getcontent_intent(self, message):
        utterance = message.data.get('utterance')
        utteranceChanged = utterance.replace(message.data.get("SendSmsGetContentKeyword"), '')
        contentString = utteranceChanged.lstrip()
        bus = dbus.SessionBus()
        remote_object = bus.get_object("org.kde.kdeconnect", "/modules/kdeconnect/devices")
        getNode = remote_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
        xmldoc = xmltodict.parse(getNode)
        try:
            for i in range(len(xmldoc['node']['node'])):
                nodeName = xmldoc['node']['node'][i]['@name']
                findNodeObject = "/modules/kdeconnect/devices/{0}".format(nodeName)
                sub_object = bus.get_object("org.kde.kdeconnect", findNodeObject)
                sub_result = sub_object.Introspect(dbus_interface="org.freedesktop.DBus.Introspectable")
                nodedoc = xmltodict.parse(sub_result)
                if 'node' in nodedoc['node'].keys():
                    nodeName = findNodeObject
        except:
                singleNode = xmldoc['node']['node']['@name']
                nodeName = "/modules/kdeconnect/devices/{0}".format(singleNode)
        telephonyPhoneNodePath = "{0}/telephony".format(nodeName)
        remote_object2 = bus.get_object("org.kde.kdeconnect", telephonyPhoneNodePath)
        remote_object2.sendSms(contactNumber, contentString, dbus_interface="org.kde.kdeconnect.device.telephony")
        
        
    def stop(self):
        pass

# The "create_skill()" method is used to create an instance of the skill.
# Note that it's outside the class itself.
def create_skill():
    return KDEConnectSkill()
