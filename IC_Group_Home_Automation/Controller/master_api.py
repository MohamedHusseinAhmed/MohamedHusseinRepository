from time import sleep
import serial
#import pymysql
import numpy as np
import libscrc
import glob
import requests
from requests.auth import HTTPBasicAuth 
import json
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import threading
import socket

base_url = 'http://localhost:9000'
token =''
email='root@root.com'
password='123456789'

groupList=[]
zoneList=[]
buttonList=[]
stateList=[]


Em_nameList=[]
Em_stateList=[]



groupCurtainList=[]
zoneCurtainList=[]
buttonCurtainList=[]
stateCurtainList=[]
NUM_BYTES_SWITCH_DATA  = 16
SWITCH_STATE_BYTE      = 12
SWITCH_ID_BYTE         = 10
write=0;
read=0;

#master_port = serial.Serial('/dev/ttyUSB1', 9600,timeout = 2) # Establish the connection on a specific port
#sensors_port = serial.Serial('/dev/ttyUSB1', 9600,timeout = 2) # Establish the connection on a specific port

ports = serial.tools.list_ports.comports()
for i in range (0, len(ports)):
    
    #if ports[i].hwid[12]=='1'and ports[i].hwid[13] == 'A' and ports[i].hwid[14]== '8' and ports[i].hwid[15] == '6':
        #print("Sensors Port connected" , ports[i].hwid)
        #print("",ports[i].device)# This is Device that's will be used to connect serial
        #sensors_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port
    if ports[i].hwid[12]=='0'and ports[i].hwid[13] == '6' and ports[i].hwid[14]== '7' and ports[i].hwid[15] == 'B':    
        print("USB to Serial Connected" , ports[i].hwid)
        print("",ports[i].device)# This is Device that's will be used to connect serial
        master_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port


state_on  = 0x010A
state_off = 0x0000

group_id  = 0x01
zone_id   = 0x03

button_1  = 0x01
button_2  = 0x02
button_3  = 0x03

usb_master = 0
#master_port = 0

usb_sensors = 0
#sensors_port = 0
x = 'first'

#response= np.array([])
#response_filtered=np.array([])
######################################
######################################


# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("devices/#")
    client.subscribe("curtains/#")
    client.subscribe("acs/#")
    client.subscribe("sensors/#")
    
# The callback function for received message


def on_message(client, userdata, msg):
    loaded_json = json.loads(msg.payload)
    top, ids = (msg.topic).split('/')
    sleep(.5)
    try:
        if top=='devices':
            GetState(msg.payload)
            print (loaded_json['group'])
            print (loaded_json['zone'])
            print (loaded_json['button'])
            print (loaded_json['value'])
            #client.publish(msg.topic, payload=json.{"value":"on"}, qos=0, retain=False)
        elif top == 'curtains':
                GetCurtainState(msg.payload)
        elif top == 'acs':
            GetACValues(msg.payload)
    except IndexError:
        print ('not found')
    except KeyError:
        print ('not found')

###############################################################################################

                                 
def Em_CreateDevice(name,state):
    data ={ 'email': email,'password': password,'name': name,'army':'on'}
    url = base_url+'/api/v1/sensors/'
    header = { 'Authorization': 'Bearer '+token}
    # call get service with headers and params
    response = requests.post(url,headers=header,data=data)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        id = loaded_json['_id']

def Em_setzones(name,state):
        device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
        url = base_url+'/api/v1/sensors/'+id
        header = { 'Authorization': 'Bearer '+str(token)}
        # call get service with headers and params
        response = requests.put(url,headers=header,data=device_body)
        if(response.status_code==200):
            return 'ok'

def Em_setState(name,state):
    listt = Em_GetTargetDevice(name)
    id=listt[0]
    print (id)
    if id !=None:
        #device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'value': state,'__v': '','name': ''}
        MQTT_MSG=json.dumps({'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'version':None,'tag': None,'army':listt[1],'intensity': None,'value': state,'__v': '','name': ''})
        client.publish("sensors/"+id, payload=MQTT_MSG)
    else:
        Em_CreateDevice(name,state)

def Em_GetTargetDevice(name):
    url = base_url+'/api/v1/sensors/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+token,'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                if item['name']==name:
                    return [item['_id'],item['army']]
            except IndexError:
                print ('not found')
            except KeyError:
                print ('not found')
                
def Em_GetState(name):
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
    if ( len(response) >0) and (response[0] == 0x53) and (response[1] == 0x45):
        if(response[2] == 0x31) and (response[5] == 0x4E):
            motion_state='on'
            Em_write_device_state_db('motion',motion_state)
            print("motion_on")
        #touch is on #SE2_ON    
        if(response[2] == 0x32) and (response[5] == 0x4E):
            touch_state='on'
            Em_write_device_state_db('touch',touch_state)
            print("touch_on")
        #window is on #SE3_ON    
        if(response[2] == 0x33) and (response[5] == 0x4E):
            window_state='on'
            Em_write_device_state_db('window',window_state)
            print("window_on")
        #gas is on #SE4_ON    
        if(response[2] == 0x34) and (response[5] == 0x4E):
            gas_state='on'
            Em_write_device_state_db('gas',gas_state)
            print("gas_on")
        #fire is on #SE5_ON    
        if(response[2] == 0x35) and (response[5] == 0x4E):
            fire_state='on'
            Em_write_device_state_db('fire',fire_state)
            print("fire_on")

        #motion is on #SE1_OFF
        if(response[2] == 0x31) and (response[5] == 0x46):
            motion_state='off'
            Em_write_device_state_db('motion',motion_state)
            #print("motion_off")
        #touch is on #SE2_OFF    
        if(response[2] == 0x32) and (response[5] == 0x46):
            touch_state='off'
            Em_write_device_state_db('touch',touch_state)
            #print("touch_off")
        #window is on #SE3_OFF    
        if(response[2] == 0x33) and (response[5] == 0x46):
            window_state='off'
            Em_write_device_state_db('window',window_state)
            #print("window_off")
        #gas is on #SE4_OFF    
        if(response[2] == 0x34) and (response[5] == 0x46):
            gas_state='off'
            Em_write_device_state_db('gas',gas_state)
            #print("gas_off")
        #fire is on #SE5_OFF    
        if(response[2] == 0x35) and (response[5] == 0x46):
            fire_state='off'
            Em_write_device_state_db('fire',fire_state)
            #print("fire_off") 

######################################
def Em_ChkState_inLists(name, state):
    for i in range(len(Em_nameList)):
        if Em_nameList[i] == name:
            if Em_stateList[i]==state:
                return True
    return False
def Em_setState_inLists(name, state):
    for i in range(len(Em_nameList)):
        if Em_nameList[i] == name:
            Em_stateList[i]=state

def Em_Chk_inLists(name):
    for i in range(len(Em_nameList)):
        if Em_nameList[i] == name:
                return True
    return False
######################################

def Em_write_device_state_db(name,sensor_state):
    #print('state => ',sensor_state)
    if Em_Chk_inLists(name)==False:
        Em_nameList.append(name)
        Em_stateList.append(sensor_state)
        Em_setState(name,sensor_state)
    else:
        if Em_ChkState_inLists( name,sensor_state)==False:
            Em_setState_inLists( name,sensor_state)
            Em_setState( name,sensor_state)
    
    
    
    
######################################
 
def Em_thread_function():
    while True:
        get_emergency_status()
        #sleep(.1)

######################################


#############################################################################################
def Login(email,password):
    data ={'email': str(email), 'password': str(password)}
    url = base_url+'/auth/local/'
    headers = {'Accept': 'application/json'}
    headers = {'Content-Type': 'application/json'}
    # call get service with headers and params
    response = requests.post(url,data=data)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        return loaded_json['token']

def CreateDevice(name,group,zone,button,state):
    data ={ 'email': email,'password': password,'name': name}
    url = base_url+'/api/v1/devices/'
    header = { 'Authorization': 'Bearer '+ str(token)}
    # call get service with headers and params
    response = requests.post(url,headers=header,data=data)
    #print (response.text)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        print(loaded_json)
        idd = loaded_json['_id']
        setzones(idd,group,zone,button,state)

def setzones(id,group,zone,button,state):
    device_body = { 'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
    url = base_url+'/api/v1/devices/'+id
    header = { 'Authorization': 'Bearer '+token}
    # call get service with headers and params
    response = requests.put(url,headers=header,data=device_body)
    #print (response.text)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        print(loaded_json)
        return 'ok'

def setState(group,zone,button,state):
    print(group)
    print(zone)
    print(button)
    idd = GetTargetDevice(group,zone,button)
    print (idd)
    if idd !=None:
        MQTT_MSG=json.dumps({'_id':idd,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''})
        client.publish("devices/"+str(idd), payload=MQTT_MSG)
    else:
        CreateDevice((str(group)+'_'+str(zone)+'_'+str(button)),group,zone,button,state)

def GetTargetDevice(group,zone,button):
    url = base_url+'/api/v1/devices/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ str(token),'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        #print("from db : ", loaded_json)
        for item in loaded_json:
            try:
                if item['zone']==zone and item['group']==group and item['button']==button:
                    return item['_id']
            except IndexError:
                print ('not found')
            except KeyError:
                print ('not found')
                
def GetState(body):
    loaded_json = json.loads(body)
    try:
        #print('zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
        if Chk_inLists((loaded_json['group']),(loaded_json['zone']),(loaded_json['button']))==False:
            groupList.append((loaded_json['group']))
            zoneList.append((loaded_json['zone']))
            buttonList.append((loaded_json['button']))
            stateList.append((loaded_json['value']))
            set_switch_state((loaded_json['group']),(loaded_json['zone']),(loaded_json['button']),(loaded_json['value']))
        else:
            if ChkState_inLists( (loaded_json['group']),(loaded_json['zone']),(loaded_json['button']),(loaded_json['value']))==False:
                setState_inLists((loaded_json['group']),(loaded_json['zone']),(loaded_json['button']),(loaded_json['value']))
                set_switch_state((loaded_json['group']),(loaded_json['zone']),(loaded_json['button']),(loaded_json['value'])) 
    except IndexError:
        print ('not found')
    except KeyError:
        print ('not found')           


#####################################Curtains###########

def CreateCurtains(name,group,zone,button,state):
    data ={'value': state, 'name': name,'group': group,'zone': zone,'button': button, 'email': email,'password': password,'name': name}
    url = base_url+'/api/v1/curtains/'
    header = { 'Authorization': 'Bearer '+token}
    response = requests.post(url,headers=header,data=data)
    #print (response.text)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)


def setCurtainState(group,zone,button,state):
    id = GetTargetCurtain(group,zone,button)
    #print (id)
    if id !=None:
        MQTT_MSG=json.dumps({'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''})
        client.publish("curtains/"+id, payload=MQTT_MSG)
    else:
        CreateCurtains((str(zone)+'_'+str(group)+'_'+str(button)),group,zone,button,state)

def GetTargetCurtain(group,zone,button):
    url = base_url+'/api/v1/curtains/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+token,'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                if item['zone']==zone and item['group']==group and item['button']==button:
                    return item['_id']
            except IndexError:
                print ('not found')
            except KeyError:
                print ('not found')
                
def GetCurtainState(body):
    item = json.loads(body)
    #print (item)
    try:
        print('Curtain => zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
        if ChkCurtain_inLists(item['group'],item['zone'],item['button'])==False:
            groupCurtainList.append(item['group'])
            zoneCurtainList.append(item['zone'])
            buttonCurtainList.append(item['button'])
            stateCurtainList.append(item['value'])
            set_curtain_state(item['group'],item['zone'],item['button'],item['value']) 
        else:
            if ChkCurtainState_inLists(item['group'],item['zone'],item['button'],item['value'])==False:
                setCurtainState_inLists(item['group'],item['zone'],item['button'],item['value'])
                set_curtain_state(item['group'],item['zone'],item['button'],item['value']) 
    except IndexError:
        print ('not found')
    except KeyError:
        print ('not found')           


######################################
def get_master_status():
    master_port.flush()
    response= np.array([0])
    response_filtered=np.array([0])
    b_response = bytearray(response)
    mx = 0
    c=0
    if write==0:
        read=1
        if(master_port.in_waiting):
            response = master_port.read(50)
            #TODO: search for a sequence
            b_response = bytearray(response)
            #print("response ",response)
            #print("response length", np.size(b_response)) 

            mx = response.find(b'\x02\x01\xE1\x09', mx)
            if mx != -1:
                print("filtered index => ",mx)

                
        response_filtered = response[mx : ]
           
        b_response_filtered = bytearray(response_filtered)
        #print("response_filtered ",response_filtered)
        #print("response_filtered length",np.size(b_response_filtered))

        read=0
        if ((np.size(b_response_filtered) > 12) and (b_response_filtered[6] == 0x12) and (b_response_filtered[7] == 0x06)):  
            get_switch_status(b_response_filtered)
        elif ((np.size(b_response_filtered) > 12) and (b_response_filtered[6] == 0x13) and (b_response_filtered[7] == 0x06)):  
            get_curtain_status(b_response_filtered)
        master_port.flush()

######################################
            
def get_switch_status(response):
    print("response switch",response)
    if ((len(response) > 12) and (response[6] == 0x12) and (response[7] == 0x06)):
        for loop_index in response:
            if (response[SWITCH_STATE_BYTE] == 0x01):
                device_state = 'on'
                button_id = response[SWITCH_ID_BYTE]
                device_group = response[8]
                device_zone = response[9]
                write_device_state_db(device_group,device_zone, button_id, device_state)
                print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
                return 'on'
            else:
                device_state='off'
                button_id = response[SWITCH_ID_BYTE]
                device_group = response[8]
                device_zone = response[9]
                write_device_state_db(device_group,device_zone, button_id, device_state)
                print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
                return 'off'
            response = 0

######################################
def set_switch_state(device_group,device_zone, button_id, device_state):
    if (device_state == 'on'):
        device_state_l = 0x01
        device_state_h = 0x0A
    elif (device_state == 'off'):
        device_state_l = 0x00
        device_state_h = 0x00
    write=1
    print("rx_zone ", device_zone)
    print("rx_group ",device_group)
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_group,device_zone,button_id,device_state_l,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_group,device_zone,button_id,device_state_l,device_state_h,(crc8+1),0x03]
    v_send_request_status = bytearray(send_request_status)
    print("sent set_switch_state ",v_send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    master_port.flush()
    response = 0
    #response = master_port.read(NUM_BYTES_SWITCH_DATA)
    #print("response set_switch_state ",response)
    #response = 0
    write=0

######################################
def get_curtain_status(response):
    print("response curtain ",response)
    print("response length", len(response))
    if ((len(response) > 12) and (response[6] == 0x13) and (response[7] == 0x06)):
        for loop_index in response:
            #device_state = response[12] #UP 0x01, Down or Stop 0x00
            #print("curtain state ",response[12])
            if response[12] == 0x01:
                device_state = 'up'
            elif response[12] == 0x00:
                device_state = 'stop'
            elif response[12] == 0x02:
                device_state = 'down'
            button_id = response[8] # no need for this 
            device_group = response[10]
            device_zone = response[9]
        write_curtain_state_db(device_group,device_zone, button_id, device_state)
        print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
        response = 0
    
######################################
def set_curtain_state(device_group,device_zone, button_id, device_state):
    if (device_state == 'up'):
        device_state_h = 0x01
    elif (device_state == 'down'):
        device_state_h = 0x00
    elif (device_state == 'stop'):
        device_state_h = 0x02
    write=1    
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x07,0x00,0x0A,0x13,0x03,button_id,device_zone,device_group,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x07,0x00,0x0A,0x13,0x03,button_id,device_zone,device_group,device_state_h,(crc8+1),0x03]
    v_send_request_status = bytearray(send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    response = 0
    master_port.flush()
    #response = master_port.read(NUM_BYTES_SWITCH_DATA)

#############################################################################
idList=[]
TargetList=[]
CurrentList=[]
powerList=[]
modeList=[]
fanList=[]

def ChkStateAC_inLists(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    print(idd,power,mode,Ttemp,Ctemp,fanSpeed)
    for i in range(len(idList)):
        if idList[i] == idd :
            if modeList[i]==mode and powerList[i]==power and TargetList[i]==Ttemp and CurrentList[i]==Ctemp and fanList[i]==fanSpeed:
                return True
    return False
def setStateAC_inLists(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    for i in range(len(idList)):
        if idList[i] == idd :
            powerList[i]=power
            modeList[i]=mode
            TargetList[i]=Ttemp
            CurrentList[i]=Ctemp
            fanList[i]=fanSpeed
            powerList[i]=power

def ChkAC_inLists(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    for i in range(len(idList)):
        if idList[i] == idd:
                return True
    return False

def CreateAC(name,idd,power,mode,Ttemp,Ctemp,fanSpeed):
    data ={'currentTemp':Ctemp ,'targetTemp':Ttemp ,'mode':mode ,'fanSpeed':fanSpeed ,'value':power,'group':idd, 'email': email,'password': password,'name': name}
    url = base_url+'/api/v1/acs/'
    header = { 'Authorization': 'Bearer '+token}
    response = requests.post(url,headers=header,data=data)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        id = loaded_json['_id']
        #setzones(id,zone,group,button,state)


def setACValues(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    #print ('Values => ',idd,power,mode,Ttemp,Ctemp,fanSpeed)
    id = GetTargetAC(idd)
    #print (id)
    if id !=None:
        MQTT_MSG=json.dumps({'_id':id ,'currentTemp':Ctemp ,'targetTemp': Ttemp,'fanSpeed': fanSpeed,'mode': mode,'value': power,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': idd,'zone': None,'__v': '','name': '','email': '','picture': '','createdBy': ''})
        client.publish("acs/"+id, payload=MQTT_MSG)
    
def GetTargetAC(id):
    url = base_url+'/api/v1/acs/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+token,'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                if item['group']==id:
                    return item['_id']
            except IndexError:
                print ('not found')
            except KeyError:
                print ('not found')
                
def GetACValues(body):
    loaded_json = json.loads(body)
    print(loaded_json)
    try:
        read_AC_state_db(loaded_json['value'],loaded_json['mode'],loaded_json['currentTemp'] ,int(loaded_json['targetTemp'] ),int(loaded_json['fanSpeed']),loaded_json['group'])
    except IndexError:
        print ('not found')
    except KeyError:
        print ('not found')           


 
############################################################################

############################################################################
# Air Conditioner
############################################################################

def calc_crc(data : bytes):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos 
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def AirCond_ReadControlPacket(AirCond_ID ,Address ,Value ,Socket):
    Packet=[0x01,0x02,0x03,0x04,0x05,0x00,0x00,0x00]
    Packet[0]=0x01 #To do : get AC ID from DT
    Packet[1]=0x03
    Packet[2]=0x00
    Packet[3]=Address
    Packet[4]=0x00
    Packet[5]=Value
    Crc = calc_crc(bytearray([Packet[0],Packet[1],Packet[2],Packet[3],Packet[4],Packet[5]]))
    #print("%04X"%(Crc))
    Packet[6]=((Crc >>8)&0x00FF)
    Packet[7]=((Crc)&0x00FF)
#    print("%04X"%(Crc))
#    print(bytearray(Packet))
    Socket.send(bytearray(Packet))
    
def AirCond_WriteControlPacket(AirCond_ID ,Address ,Value,Socket ):
    Packet=[0x01,0x02,0x03,0x04,0x05,0x00,0x00,0x00]
    Packet[0]=AirCond_ID 
    Packet[1]=0x06
    Packet[2]=0x00
    Packet[3]=Address
    Packet[4]=0x00
    Packet[5]=Value
    Crc = calc_crc(bytearray([Packet[0],Packet[1],Packet[2],Packet[3],Packet[4],Packet[5]]))
#    print("%04X"%(Crc))
    Packet[7]=((Crc >>8)&0x00FF)
    Packet[6]=((Crc)&0x00FF)
    Socket.send(bytearray(Packet))
    print("sent ",Packet[0],Packet[1],Packet[2],Packet[3],Packet[4],Packet[5],Packet[6],Packet[7],)
    try:
        received = Socket.recv(1024)
    except socket.timeout:
        print("Timeout raised and caught.")
 

def AirCond_StatusPacket(AirCond_ID,Socket):
    print("AirCond_ID", AirCond_ID)
    Packet=[0x01,0x02,0x03,0x04,0x05,0x00,0x00,0x00]
    Packet[0]=AirCond_ID
    Packet[1]=0x03
    Packet[2]=0x00
    Packet[3]=0x00
    Packet[4]=0x00
    Packet[5]=0x05
    Crc = calc_crc(bytearray([Packet[0],Packet[1],Packet[2],Packet[3],Packet[4],Packet[5]]))
#    print("%04X"%(Crc))
    Packet[7]=((Crc >>8)&0x00FF)
    Packet[6]=((Crc)&0x00FF)
    Socket.sendall(bytearray(Packet)) 
    print("status packet ",bytearray(Packet))

def AirCond_GetStatusPacket(Received_Packet):
    if(len(Received_Packet) > 13):
        AC_ID = Received_Packet[0]
        AC_Status = Received_Packet[4]
        AC_CurrentTemp = Received_Packet[6]
        AC_TargetTemp = Received_Packet[8]
        AC_Mode = Received_Packet[10]
        AC_Fan  =  Received_Packet[12]
        write_AC_state_db(AC_ID,AC_Status,AC_CurrentTemp,AC_TargetTemp ,AC_Mode,AC_Fan)
        

##################################################
#
##################################################
def write_AC_state_db(AC_ID,AC_Status,AC_CurrentTemp,AC_TargetTemp ,AC_Mode,AC_Fan):
    state=''
    mode=''
    if AC_Status==1:
        state='on'
    elif AC_Status==0:
        state='off'
    
    if AC_Mode==1:
        mode='cool'
    elif AC_Mode==0:
        mode='fan'
    elif AC_Mode==2:
        mode='heat'
        
    if ChkAC_inLists(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
        idList.append(AC_ID)
        powerList.append(state)
        modeList.append(mode)
        TargetList.append(AC_TargetTemp)
        CurrentList.append(AC_CurrentTemp)
        fanList.append(AC_Fan)
    else:
        if ChkStateAC_inLists(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
            setStateAC_inLists(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)
            setACValues(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)
            print(AC_ID,AC_Status,AC_CurrentTemp,AC_TargetTemp ,AC_Mode,AC_Fan)
##################################################
def read_AC_state_db(AC_Status,AC_Mode,AC_CurrentTemp,AC_TargetTemp,AC_Fan,AC_ID):
    #item['value'],item['mode'] ,item['currentTemp'] ,item['targetTemp'] ,item['fanSpeed'],item['group'] 
    #idd,power,mode,Ttemp,Ctemp,fanSpeed)
    print(idList)
    for i in range(len(idList)):
        print(AC_ID)
        if idList[i] == AC_ID :
           if modeList[i] != AC_Mode:
               if(AC_Mode == 'cool'):
                 AirCond_WriteControlPacket(AC_ID ,0x03 ,0x01 ,AirCond_socket)  
               elif(AC_Mode == 'fan'):
                 AirCond_WriteControlPacket(AC_ID ,0x03 ,0x00 ,AirCond_socket)
               elif(AC_Mode == 'heat'):
                 AirCond_WriteControlPacket(AC_ID ,0x03 ,0x02 ,AirCond_socket)
                
           elif powerList[i]!=AC_Status:
               if(AC_Status == 'on'):
                   AirCond_WriteControlPacket(AC_ID ,0x00 ,0x01 ,AirCond_socket)  
               elif(AC_Status == 'off'):
                   AirCond_WriteControlPacket(AC_ID ,0x00 ,0x00 ,AirCond_socket)
                
           elif TargetList[i]!=AC_TargetTemp:
               AirCond_WriteControlPacket(AC_ID ,0x02 , AC_TargetTemp ,AirCond_socket) 
                  
           elif fanList[i]!=AC_Fan:
               AirCond_WriteControlPacket(AC_ID ,0x04 , AC_Fan ,AirCond_socket)
        
  
        
    #print("DB => ",AC_Status,AC_Mode,AC_CurrentTemp,AC_TargetTemp,AC_Fan,AC_ID)
    if ChkAC_inLists(AC_ID,AC_Status,AC_Mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
        idList.append(AC_ID)
        powerList.append(AC_Status)
        modeList.append(AC_Mode)
        TargetList.append(AC_TargetTemp)
        CurrentList.append(AC_CurrentTemp)
        fanList.append(AC_Fan)


    else:
         if ChkStateAC_inLists(AC_ID,AC_Status,AC_Mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
            setStateAC_inLists(AC_ID,AC_Status,AC_Mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)
            print("I'm in Else & if ")
        
      
##################################################

def AirCond_SocketComm(portNo,Str_Ip,Socket):
    Socket.connect((Str_Ip, portNo))
    Socket.settimeout(1)
    # receive Init Message from Sena Dummy Receive
    received = Socket.recv(1024)
    print("received",received) 


###############################################################################
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

def ChkCurtainState_inLists(group,zone, button, state):
    for i in range(len(groupCurtainList)):
        if groupCurtainList[i] == group and zoneCurtainList[i] == zone and buttonCurtainList[i] == button:
            if stateCurtainList[i]==state:
                return True
    return False
def setCurtainState_inLists(group,zone, button, state):
    for i in range(len(groupCurtainList)):
        if groupCurtainList[i] == group and zoneCurtainList[i] == zone and buttonCurtainList[i] == button:
            stateCurtainList[i]=state

def ChkCurtain_inLists(group,zone, button):
    for i in range(len(groupCurtainList)):
        if groupCurtainList[i] == group and zoneCurtainList[i] == zone and buttonCurtainList[i] == button:
                return True
    return False
######################################

def write_device_state_db(device_group,device_zone, button_id, device_state):
    setState(device_group ,device_zone,button_id,device_state)
    return
######################################

def write_curtain_state_db(device_group,device_zone, button_id, device_state):
    setCurtainState(device_group,device_zone,button_id,device_state)
    return
######################################
def read_device_state_db(device_name,device_zone,device_group):
    return device_state
#####################################
def thread_function():
    client.loop_forever()

def thread_functionAC():
    while True:
        #GetACValues()
        #setACValues(1,'on','cool',20,16,2)
        #print(idList)
        for i in range(len(idList)):
            try:
                sleep(1)
                AirCond_StatusPacket(idList[i],AirCond_socket)
                AirCond_GetStatusPacket(AirCond_socket.recv(1024))
                sleep(1)
            except socket.timeout:
                print("Timeout raised and caught.")
        

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")

######################################
HOST = '192.168.1.150'
#HOST = '192.168.1.150'    
PORT = 7001
AirCond_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("AirCond_socket",AirCond_socket)
AirCond_SocketComm(PORT,HOST,AirCond_socket)


    
if __name__ == '__main__':
    token = Login(email,password)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect("localhost", 1883, 30)
    
    x = threading.Thread(target=thread_function)
    x.start()
    #setState(3,1,9,'on')
    ac = threading.Thread(target=thread_functionAC)
    ac.start()
    #em = threading.Thread(target=Em_thread_function)
    #em.start()
    #client.loop_forever()
    while True:
        #device_group,device_zone, button_id
        get_master_status()
        #print (groupCurtainList)
        #print (zoneCurtainList)
        #print (buttonCurtainList)
        #print (stateCurtainList)
        sleep(.2)
    