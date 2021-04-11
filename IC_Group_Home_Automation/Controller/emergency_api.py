from time import sleep
import serial
#import pymysql
import numpy
import libscrc
import glob
import requests
from requests.auth import HTTPBasicAuth 
import json
import serial.tools.list_ports

base_url = 'http://localhost:9001'
token =''
email='root@root.com'
password='123456789'
groupList=[]
zoneList=[]
buttonList=[]
stateList=[]

groupCurtainList=[]
zoneCurtainList=[]
buttonCurtainList=[]
stateCurtainList=[]

ports = serial.tools.list_ports.comports()

for i in range (0, len(ports)):
    
    if ports[i].hwid[12]=='1'and ports[i].hwid[13] == 'A' and ports[i].hwid[14]== '8' and ports[i].hwid[15] == '6':
        print("Sensors Port connected" , ports[i].hwid)
        print("",ports[i].device)# This is Device that's will be used to connect serial
        sensors_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port
   # elif ports[i].hwid[12]=='0'and ports[i].hwid[13] == '6' and ports[i].hwid[14]== '7' and ports[i].hwid[15] == 'B':    
   #     print("USB to Serial Connected" , ports[i].hwid)
   #     print("",ports[i].device)# This is Device that's will be used to connect serial
   #     master_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port

usb_master = 0
#master_port = 0

usb_sensors = 0
#sensors_port = 0
x = 'first'

response = numpy.array([])
######################################




def Login(email,password):
    data ={'email': email, 'password': password}
    url = base_url+'/auth/local/'
    headers = {'Accept': 'application/json'}
    headers = {'Content-Type': 'application/json'}
    # call get service with headers and params
    response = requests.post(url,data=data)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        return loaded_json['token']
                                 
def CreateDevice(name,state):
    data ={ 'email': email,'password': password,'name': name}
    url = base_url+'/api/v1/sensors/'
    header = { 'Authorization': 'Bearer '+token}
    # call get service with headers and params
    response = requests.post(url,headers=header,data=data)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        id = loaded_json['_id']

def setzones(name,state):
        device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
        url = base_url+'/api/v1/sensors/'+id
        header = { 'Authorization': 'Bearer '+str(token)}
        # call get service with headers and params
        response = requests.put(url,headers=header,data=device_body)
        if(response.status_code==200):
            return 'ok'

def setState(name,state):
    id = GetTargetDevice(name)
    print (id)
    if id !=None:
        device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'value': state,'__v': '','name': ''}
        url = base_url+'/api/v1/sensors/'+id
        header = { 'Authorization': 'Bearer '+token}
        # call get service with headers and params
        response = requests.put(url,headers=header,data=device_body)
        print(response.text)
        if(response.status_code==200):
            return ('ok')
    else:
        CreateDevice(name,state)

def GetTargetDevice(name):
    url = base_url+'/api/v1/sensors/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+token,'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                if item['name']==name:
                    return item['_id']
            except IndexError:
                print ('not found')
            except KeyError:
                print ('not found')
                
def GetState(name):
    url = base_url+'/api/v1/sensors/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+str(token),'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                if item['name']==name:
                    return item['value']
            except IndexError:
                print ('not found')
            except KeyError:
                print ('not found' )          






######################################

def get_emergency_status():
    response = 0
    sensors_port.flush()
    response = sensors_port.readline()
    print(response)

    #motion is on #SE1_ON
    if (response[0] == 0x53) and (response[1] == 0x45):
        if(response[2] == 0x31) and (response[5] == 0x4E):
            motion_state='on'
            write_device_state_db('motion',motion_state)
            print("motion_on")
        #touch is on #SE2_ON    
        if(response[2] == 0x32) and (response[5] == 0x4E):
            touch_state='on'
            write_device_state_db('touch',touch_state)
            print("touch_on")
        #window is on #SE3_ON    
        if(response[2] == 0x33) and (response[5] == 0x4E):
            window_state='on'
            write_device_state_db('window',window_state)
            print("window_on")
        #gas is on #SE4_ON    
        if(response[2] == 0x34) and (response[5] == 0x4E):
            gas_state='on'
            write_device_state_db('gas',gas_state)
            print("gas_on")
        #fire is on #SE5_ON    
        if(response[2] == 0x35) and (response[5] == 0x4E):
            fire_state='on'
            write_device_state_db('fire',fire_state)
            print("fire_on")

        #motion is on #SE1_OFF
        if(response[2] == 0x31) and (response[5] == 0x46):
            motion_state='off'
            write_device_state_db('motion',motion_state)
            print("motion_off")
        #touch is on #SE2_OFF    
        if(response[2] == 0x32) and (response[5] == 0x46):
            touch_state='off'
            write_device_state_db('touch',touch_state)
            print("touch_off")
        #window is on #SE3_OFF    
        if(response[2] == 0x33) and (response[5] == 0x46):
            window_state='off'
            write_device_state_db('window',window_state)
            print("window_off")
        #gas is on #SE4_OFF    
        if(response[2] == 0x34) and (response[5] == 0x46):
            gas_state='off'
            write_device_state_db('gas',gas_state)
            print("gas_off")
        #fire is on #SE5_OFF    
        if(response[2] == 0x35) and (response[5] == 0x46):
            fire_state='off'
            write_device_state_db('fire',fire_state)
            print("fire_off") 

######################################
def ChkState_inLists(group,zone, button, state):
    for i in range(len(groupList)):
        if groupList[i] == group and zoneList[i] == zone and buttonList[i] == button:
            if stateList[i]==state:
                return True
    return False
def setState_inLists(group,zone, button, state):
    for i in range(len(groupList)):
        if groupList[i] == group and zoneList[i] == zone and buttonList[i] == button:
            stateList[i]=state

def Chk_inLists(group,zone, button):
    for i in range(len(groupList)):
        if groupList[i] == group and zoneList[i] == zone and buttonList[i] == button:
                return True
    return False
######################################

def write_device_state_db(name,sensor_state):
    print('state => ',sensor_state)
    setState(name,sensor_state)
    
######################################
 

######################################
if __name__ == '__main__':
    token = Login(email,password)
    #setState(3,1,9,'on')
    while True:
        get_emergency_status()
        sleep(1)
    
  