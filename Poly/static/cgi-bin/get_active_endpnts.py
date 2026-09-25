#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import sys
import codecs
import datetime
import csv
import subprocess

IPCollection = set()
IPCollectionCount = 0
RowCounter = 1
EndpointCollection = set()
NameCollection = []
VPNNameCollection = []
VPN = []
MapNames = []
noncompArr = []
KSUIT_New = []
KSUIT=[]
KSUIT_Rows=[]
keyarr = 0
counter = 1
sumNoncomp = 0
endpoints = {}
endpoint2 = []
url = "https://spb99-vcsdm.gazprom-neft.local/api/rest/devices/?page=" + str(counter)
header ="No"+","+"deviceIdentifier"+","+"deviceName"+","+"deviceModel"+","+"deviceVersion"+","+"registrationIdentifier"+","+"allowInactivityDeletion"+","+"supportsH323"+","+"supportsSip"+","+"hasMcuCapabilities"+","+"ipAddress"+","+"entityTag"+","+"site"+","+"sipUri"+","+"sipActive"+","+"sipRegistrationState"+","+"h323Alias"+","+"registrationActive"+","+"h323RegistrationState"+","+"E164"+","+"neverDeleteDueToInactivity"+","+"complianceLevel""\n"

def mapdevices():
        global MapNames
        for value in VPNNameCollection:
                MapNames += value
                keyarr += 1
        DeviceArrValue = 1


def zeros():
        global deviceIdentifier
        global sumNoncomp
        global sipUri
        global sipActive
        global sipRegistrationState
        global deviceName
        global deviceModel
        global deviceVersion
        global registrationIdentifier
        global allowInactivityDeletion
        global supportsH323
        global supportsSip
        global hasMcuCapabilities
        global ipAddress
        global entityTag
        global site
        global h323Alias
        global registrationActive
        global h323RegistrationState
        global E164
        global neverDeleteDueToInactivity
        global complianceLevel
        deviceIdentifier = ''
        deviceAdmissionPolicy = ''
        sipUri = ''
        sipActive = ''
        sipRegistrationState = ''
        deviceName = ''
        deviceModel = ''
        deviceVersion = ''
        registrationIdentifier = ''
        allowInactivityDeletion = ''
        supportsH323 = ''
        supportsSip = ''
        hasMcuCapabilities = ''
        ipAddress = ''
        entityTag = ''
        site = ''
        h323Alias = ''
        registrationActive = ''
        h323RegistrationState = ''
        E164 = ''
        neverDeleteDueToInactivity = ''
        complianceLevel = ''


def main():
        global endpoint2
        global endpoints
        global sumNoncomp
        global deviceName
        global url
        global counter
        global RowCounter
        global IPCollectionCount
        global EndpointCollection
        global sipUri
        global sipActive
        global NameCollection
        global sipRegistrationState
        global noncompFile
        global registrationActive
        global deviceIdentifier
        global deviceModel
        global deviceVersion
        global registrationIdentifier
        global allowInactivityDeletion
        global supportsH323
        global supportsSip
        global hasMcuCapabilities
        global entityTag
        global site
        global h323Alias
        global registrationActive
        global h323RegistrationState
        global E164
        global ipAddress
        global neverDeleteDueToInactivity
        global complianceLevel
        global deviceAdmissionPolicy
        currentPage = 1
        date = datetime.datetime.today()
        while currentPage != 0:
                url = "https://spb99-vcsdm.gazprom-neft.local/api/rest/devices/?page=" + str(counter)
                req = requests.get(url, headers={'dataType': 'json',"Authorization": "Basic YWRtaW5GUzpWazQyTGZCaA==",'Accept': 'application/vnd.plcm.plcm-device-list-v3+json','contentType': 'application/json'})
                data1 = req.json()
                data2 = json.dumps(data1, indent=2)
                elem = json.loads(data2)
                currentPage = elem['plcmPage']['currentPage']
                if currentPage == 0:
                        break
                counter+=1
                for row in elem['plcmDeviceV3List']:
                        zeros()
                        for column in row:
                                if column == 'deviceAdmissionPolicy':
                                        deviceAdmissionPolicy = row['deviceAdmissionPolicy']
                                if column == 'deviceIdentifier':
                                        deviceIdentifier = row['deviceIdentifier']
                                elif column == 'deviceName':
                                        deviceName = row['deviceName']
                                elif column == 'deviceModel':
                                        deviceModel = row['deviceModel']
                                elif column == 'deviceVersion':
                                        deviceVersion = "v_" + row['deviceVersion']
                                elif column == 'registrationIdentifier':
                                        registrationIdentifier = row['registrationIdentifier']
                                elif column == 'allowInactivityDeletion':
                                        allowInactivityDeletion = row['allowInactivityDeletion']
                                elif column == 'supportsH323':
                                        supportsH323 = row['supportsH323']
                                elif column == 'supportsSip':
                                        supportsSip = row['supportsSip']
                                elif column == 'hasMcuCapabilities':
                                        hasMcuCapabilities = row['hasMcuCapabilities']
                                elif column == 'ipAddress':
                                        ipAddress = 'None'
                                        if row['ipAddress'].find(",") != -1:
                                                ipAddress = row['ipAddress'][row['ipAddress'].find(",")+1:]
                                        else:
                                                ipAddress = row['ipAddress']
                                elif column == 'entityTag':
                                        entityTag = row['entityTag']
                                elif column == 'site':
                                        site = row['site']
                                elif column == 'complianceLevel':
                                        complianceLevel = row['complianceLevel']
                                elif column == 'neverDeleteDueToInactivity':
                                        neverDeleteDueToInactivity = row['neverDeleteDueToInactivity']
                                elif column == 'plcmSipIdentityV2':
                                        sipUri = row['plcmSipIdentityV2']['sipUri']
                                        sipActive = row['plcmSipIdentityV2']['sipActive']
                                        sipRegistrationState = row['plcmSipIdentityV2']['sipRegistrationState']
                                elif column == 'plcmH323Identity':
                                        h323RegistrationState = row['plcmH323Identity']['h323RegistrationState']
                                        registrationActive = row['plcmH323Identity']['registrationActive']

                        if deviceModel != 'Polycom RealPresence Desktop for Windows' and deviceModel != 'HarmanMediaSuite':
                                if site != 'Internet/VPN/WAN':
                                        IPCollection.add(ipAddress)
                                        endpoints[ipAddress] = row['deviceAdmissionPolicy']
                                        if len(IPCollection) > IPCollectionCount:
                                                CompiledRow=str(RowCounter)+","+str(deviceIdentifier)+","+str(deviceName)+","+str(deviceModel)+","+str(deviceVersion)+","+str(registrationIdentifier)+","+str(allowInactivityDeletion)+","+str(supportsH323)+","+str(supportsSip)+","+str(hasMcuCapabilities)+","+str(ipAddress)+","+str(entityTag)+","+str(site)+","+str(sipUri)+","+str(sipActive)+","+str(sipRegistrationState)+","+str(h323Alias)+","+str(registrationActive)+","+str(h323RegistrationState)+","+str(E164)+","+str(complianceLevel)+","+str(neverDeleteDueToInactivity)+","+str(deviceAdmissionPolicy)
                                                RowCounter += 1
                                                IPCollectionCount += 1
                                                EndpointCollection.add(CompiledRow)
                                                if (deviceName in VPNNameCollection):
                                                        index = VPNNameCollection.index(deviceName)
                                                        VPNNameCollection.pop(index)
                                                NameCollection.append(deviceName)
                                elif ('PolycomRealPresenceGroup' not in deviceModel):
                                        endpoints[ipAddress] = row['deviceAdmissionPolicy']
                                        if (deviceName not in NameCollection):
                                                VPNrow = str(deviceIdentifier)+","+str(deviceName)+","+str(deviceModel)+","+str(deviceVersion)+","+str(registrationIdentifier)+","+str(allowInactivityDeletion)+","+str(supportsH323)+","+str(supportsSip)+","+str(hasMcuCapabilities)+","+str(ipAddress)+","+str(entityTag)+","+str(site)+","+str(sipUri)+","+str(sipActive)+","+str(sipRegistrationState)+","+str(h323Alias)+","+str(registrationActive)+","+str(h323RegistrationState)+","+str(E164)+","+str(complianceLevel)+","+str(neverDeleteDueToInactivity)+","+str(deviceAdmissionPolicy)
                                                VPN.append(VPNrow)
                                                NameCollection.append(deviceName)
                                                VPNNameCollection.append(deviceName)
        for row in EndpointCollection:
                endpoint2.append(row)


        for item in VPN:
                WriteStr = str(RowCounter) + "," + item
                endpoint2.append(WriteStr)
                RowCounter += 1

        return(endpoints, endpoint2)
main()

