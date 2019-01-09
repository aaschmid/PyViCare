from requests_oauthlib import OAuth2Session
import requests
import re
import json

client_id = '79742319e39245de5f91d15ff4cac2a8';
client_secret = '8ad97aceb92c5892e102b093c7c083fa';
authorizeURL = 'https://iam.viessmann.com/idp/v1/authorize';
token_url = 'https://iam.viessmann.com/idp/v1/token';
apiURLBase = 'https://api.viessmann-platform.io';
redirect_uri = "vicare://oauth-callback/everest";
viessmann_scope=["openid"]

class PyViCare:
    
    return_values = {
      "heating.sensors.temperature.outside": "Ford",
      "model": "Mustang"
    }
    def __init__(self, username, password):
        self.oauth=self.getAccessToken(username, password)
        self.getInstallations()
        
    def getAccessToken(self, username, password):
        oauth = OAuth2Session(client_id, redirect_uri=redirect_uri,scope=viessmann_scope)
        authorization_url, state = oauth.authorization_url(authorizeURL)
        codestring=""
        try:
            header = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(authorization_url, headers=header,auth=(username, password))
        except Exception as e:
            #print e
            #capture the error, which contains the code the authorization code and put this in to codestring
            codestring = "{0}".format(str(e.args[0])).encode("utf-8");
            codestring = str(codestring)
            match = re.search("code\=(.*)\&",codestring)
            codestring=match.group(1)
        oauth.fetch_token(token_url, client_secret=client_secret,authorization_response=authorization_url,code=codestring)
        #r = oauth.get(apiURLBase+"/general-management/installations?expanded=true&")
        #print r.content
        return oauth
        
    def getInstallations(self):
        r = self.oauth.get(apiURLBase+"/general-management/installations?expanded=true&")
        self.installations=json.loads(r.content)
        self.href=self.installations["entities"][0]["links"][0]["href"]
        self.id=self.installations["entities"][0]["properties"]["id"]
        self.serial=self.installations["entities"][0]["entities"][0]["properties"]["serial"]
        return self.installations
    
    def jsonParsing(self,dct):
        if 'isEnabled' in dct:
            return dct["isEnabled"]
        if 'properties' in dct:
            return dct["properties"]
        if 'temperature' in dct:
            return dct["temperature"]
        if 'value' in dct:
            return dct["value"]
        if 'active' in dct:
            return dct["active"]
        if 'status' in dct:
            return dct["status"]
        return dct
    
    def getProperty2(self,property_name):
        url = apiURLBase + '/operational-data/installations/' + str(self.id) + '/gateways/' + str(self.serial) + '/devices/0/features/' + property_name
        r=self.oauth.get(url)
        j=json.loads(r.content,object_hook=self.jsonParsing)
        return j
    
    def getProperty(self,property_name):
        url = apiURLBase + '/operational-data/installations/' + str(self.id) + '/gateways/' + str(self.serial) + '/devices/0/features/' + property_name
        r=self.oauth.get(url)
        j=json.loads(r.content)
        return j
        
    def getOutsideTemperature(self):
        r=self.getProperty("heating.sensors.temperature.outside")
        return r["properties"]["value"]["value"]
        
    def getBoilerTemperature(self):
        r=self.getProperty("heating.boiler.sensors.temperature.main")
        return r["properties"]["value"]["value"]
    
    def getActiveProgram(self):
        r=self.getProperty("heating.circuits.0.operating.programs.active")
        return r["properties"]["value"]["value"]
        
    def getCurrentDesiredTemperature(self):
        r=self.getProperty("heating.circuits.0.operating.programs."+self.getActiveProgram())
        return r["properties"]["temperature"]["value"]
        
    def getDomesticHotWaterConfiguredTemperature(self):
        r=self.getProperty("heating.dhw.temperature")
        return r["properties"]["value"]["value"]
    
    def getDomesticHotWaterCurrentState(self):
        return self.getProperty("heating.circuits.0.operating.modes.dhw")["properties"]["active"]["value"]
        
    def getDomesticHotWaterStorageTemperature(self):
        return self.getProperty("heating.dhw.sensors.temperature.hotWaterStorage")["properties"]["value"]["value"]  
    