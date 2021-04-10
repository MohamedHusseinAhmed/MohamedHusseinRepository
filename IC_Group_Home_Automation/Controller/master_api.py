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
NUM_BYTES_SWITCH_DATA  = 16
SWITCH_STATE_BYTE      = 12
SWITCH_ID_BYTE         = 10


#master_port = serial.Serial('/dev/ttyUSB1', 9600,timeout = 2) # Establish the connection on a specific port
#sensors_port = serial.Serial('/dev/ttyUSB0', 9600,timeout = 2) # Establish the connection on a specific port

ports = serial.tools.list_ports.comports()

for i in range (0, len(ports)):
    
    if ports[i].hwid[12]=='1'and ports[i].hwid[13] == 'A' and ports[i].hwid[14]== '8' and ports[i].hwid[15] == '6':
        print("Sensors Port connected" , ports[i].hwid)
        print("",ports[i].device)# This is Device that's will be used to connect serial
        sensors_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port
    elif ports[i].hwid[12]=='0'and ports[i].hwid[13] == '6' and ports[i].hwid[14]== '7' and ports[i].hwid[15] == 'B':    
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

response = numpy.array([])
######################################
######################################
######################################
"""
def assign_usb_port():
    global usb_master
    global usb_sensors
    global master_port
    global sensors_port
    global x
    
    response = 0
   
    ports = glob.glob('/dev/ttyU*')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
         
    if(len(result) > 0):
        loop_index = 0
        for loop_index in result:
            master_port = serial.Serial(loop_index, 9600,timeout = 1)
            if(usb_master != 'MASTER'):
                test_switch_state(0x00,0x00,0x00,'off')
                print('one')
            response = master_port.read(NUM_BYTES_SWITCH_DATA)
            print(loop_index, response)
            if ((len(response) > 0) and (usb_master != 'MASTER') and (response[6] == 0x12) and (response[7] == 0x04)):
                master_port = serial.Serial(loop_index, 9600,timeout = 1)
                usb_master = 'MASTER'
                print('USB0_MASTER')
            if((len(response) > 0) and (usb_sensors != 'SENSORS') and (response[0] == "S") and (response[0] == "E")):
                sensors_port = serial.Serial(loop_index, 9600,timeout = 1)
                usb_sensors = 'SENSORS'
                print('USB0_SENSORS')
            else:
                print("USB0_NotFound")
            print(result)     
 """


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
        id = loaded_json['_id']
        setzones(id,zone,group,button,state)

def setzones(id,group,zone,button,state):
    device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
    url = base_url+'/api/v1/devices/'+id
    header = { 'Authorization': 'Bearer '+token}
    # call get service with headers and params
    response = requests.put(url,headers=header,data=device_body)
    #print (response.text)
    if(response.status_code==200):
        return 'ok'

def setState(group,zone,button,state):
    id = GetTargetDevice(group,zone,button)
    #print (id)
    if id !=None:
        device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': None,'zone': None,'button': None,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
        url = base_url+'/api/v1/devices/'+id
        header = { 'Authorization': 'Bearer '+token}
        # call get service with headers and params
        response = requests.put(url,headers=header,data=device_body)
        if(response.status_code==200):
            return 'ok'
    else:
        CreateDevice((str(group)+'_'+str(zone)+'_'+str(button)),group,zone,button,state)

def GetTargetDevice(group,zone,button):
    url = base_url+'/api/v1/devices/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ str(token),'Accept-Language': 'en_US'}
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
                
def GetState():
    url = base_url+'/api/v1/devices/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+str(token),'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                #print('zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
                if Chk_inLists(item['group'],item['zone'],item['button'])==False:
                    groupList.append(item['group'])
                    zoneList.append(item['zone'])
                    buttonList.append(item['button'])
                    stateList.append(item['value'])
                else:
                    if ChkState_inLists(item['group'],item['zone'],item['button'],item['value'])==False:
                        setState_inLists(item['group'],item['zone'],item['button'],item['value'])
                        set_switch_state(item['group'], item['zone'], item['button'],  item['value']) 
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
        device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': None,'zone': None,'button': None,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
        url = base_url+'/api/v1/curtains/'+id
        header = { 'Authorization': 'Bearer '+token}
        response = requests.put(url,headers=header,data=device_body)
        if(response.status_code==200):
            return 'ok'
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
                
def GetCurtainState():
    url = base_url+'/api/v1/curtains/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+str(token),'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        #print (loaded_json)
        for item in loaded_json:
            try:
                print('Curtain => zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
                if ChkCurtain_inLists(item['group'],item['zone'],item['button'])==False:
                    groupCurtainList.append(item['group'])
                    zoneCurtainList.append(item['zone'])
                    buttonCurtainList.append(item['button'])
                    stateCurtainList.append(item['value'])
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
    response = 0
    response = master_port.read(13)
    master_port.flush()
    print("response master",response)
    print("response master length",len(response))
    if ((len(response) > 12) and (response[6] == 0x12) and (response[7] == 0x06)):  
        get_switch_status(response)
    elif ((len(response) > 12) and (response[6] == 0x13) and (response[7] == 0x06)):  
        get_curtain_status(response)   

######################################
            
def get_switch_status(response):
    print("response switch",response)
    if ((len(response) > 12) and (response[6] == 0x12) and (response[7] == 0x06)):
        for loop_index in response:
            if (response[SWITCH_STATE_BYTE] == 0x01):
                device_state = 'on'
                button_id = response[SWITCH_ID_BYTE]
                device_group = response[9]
                device_zone = response[8]
                write_device_state_db(device_group,device_zone, button_id, device_state)
                #print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
                return 'on'
            else:
                device_state='off'
                button_id = response[SWITCH_ID_BYTE]
                device_group = response[9]
                device_zone = response[8]
                write_device_state_db(device_group,device_zone, button_id, device_state)
                #print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
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
    print("rx_zone ", device_zone)
    print("rx_group ",device_group)
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_zone,device_group,button_id,device_state_l,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_zone,device_group,button_id,device_state_l,device_state_h,crc8,0x03]
    v_send_request_status = bytearray(send_request_status)
    print("sent set_switch_state ",v_send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    master_port.flush()
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    print("response set_switch_state ",response)
    response = 0

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
        #print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
        response = 0
    
######################################
def set_curtain_state(device_group,device_zone, button_id, device_state):
    if (device_state == 'up'):
        device_state_h = 0x01
    elif (device_state == 'down'):
        device_state_h = 0x00
    elif (device_state == 'stop'):
        device_state_h = 0x02
        
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x07,0x00,0x0A,0x13,0x03,button_id,device_zone,device_group,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x07,0x00,0x0A,0x13,0x03,button_id,device_zone,device_group,device_state_h,crc8,0x03]
    v_send_request_status = bytearray(send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    print("response set_curtain_state ",response)
    response = 0

######################################

def get_emergency_status():
    sensors_port.flush()
    response = 0
    response = sensors_port.read(14)
    print(response)
    for x in response:
        #print(x)
        if ((response[0] == "S") and (response[1] == "E") and (response[2] == "1") and (response[5] == "N")): #S1N
            motion_1_state='on'
            print("motion_1")
        if ((response[0] == "S") and (response[1] == "E") and (response[2] == "2") and (response[5] == "N")): #S2N
            motion_2_state='on'
            print("motion_2")
        if ((response[0] == "S") and (response[1] == "E") and (response[2] == "1") and (response[5] == "F")): #S1F
            motion_1_state='off'
            print("motion_1")
        if ((response[0] == "S") and (response[1] == "E") and (response[2] == "2") and (response[5] == "F")): #S2F
            motion_2_state='off'
            print("motion_2")
    response = 0
   


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
    setState(device_group,device_zone,button_id,device_state)
    return
######################################

def write_curtain_state_db(device_group,device_zone, button_id, device_state):
    setCurtainState(device_group,device_zone,button_id,device_state)
    return
######################################
def read_device_state_db(device_name,device_zone,device_group):
    return device_state
######################################
######################################
def test_switch_state(device_group,device_zone, button_id, device_state):

    
    if (device_state == 'on'):
        device_state_l = 0x01
        device_state_h = 0x0A
    elif (device_state == 'off'):
        device_state_l = 0x00
        device_state_h = 0x00
    
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_zone,device_group,button_id,device_state_l,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_zone,device_group,button_id,device_state_l,device_state_h,crc8,0x03]
    v_send_request_status = bytearray(send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    response = 0
    #response = master_port.read(NUM_BYTES_SWITCH_DATA)
    #print("response set_switch_state ",response)

######################################
if __name__ == '__main__':
    token = Login(email,password)
    #setState(3,1,9,'on')
    while True:
        #device_group,device_zone, button_id
        get_master_status()
        #get_switch_status()
        sleep(.1)
        GetState()
        """
        set_curtain_state(0x01,0x01,0x01,'up')
        """
        #get_curtain_status()
        GetCurtainState();
        print (groupList)
        print (zoneList)
        print (buttonList)
        print (stateList)
        
        #set_switch_All(0x01, 0x03,'off')
        #set_switch_state(0x01, 0x03, 0x01, 'on')
        #get_emergency_status()
        sleep(1)
    
    
""" 
while True:
    #device_group,device_zone, button_id
    #get_switch_status(0x01, 0x03, 0x01)

    #Firstly check the usb is connected and working 
    if(usb_master != 'MASTER') or (usb_sensors != 'SENSORS') :
        assign_usb_port()

    if(usb_master == 'MASTER'):
        #set_switch_All(0x01, 0x03,'off')
        #set_switch_state(0x01, 0x03, 0x01, 'on')
        print('MASTER_alive')
    if(usb_sensors == 'SENSORS'):
        print('SENSORS_alive')

    sleep(1)
"""