from time import sleep
import serial
#import pymysql
import numpy
import libscrc
import glob
import requests
from requests.auth import HTTPBasicAuth 
import json
# Import socket module
import socket

base_url = 'http://localhost:9000'
token =''
email='root@root.com'
password='123456789'
groupList=[]
zoneList=[]
buttonList=[]
stateList=[]
NUM_BYTES_SWITCH_DATA  = 16
SWITCH_STATE_BYTE      = 12
SWITCH_ID_BYTE         = 10


master_port = serial.Serial('/dev/ttyUSB0', 9600,timeout = 1) # Establish the connection on a specific port
sensors_port = serial.Serial('/dev/ttyUSB0', 9600,timeout = 1) # Establish the connection on a specific port

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
    print (response.text)
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
    print (response.text)
    if(response.status_code==200):
        return 'ok'

def setState(group,zone,button,state):
    id = GetTargetDevice(group,zone,button)
    print (id)
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
                print('zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
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




######################################
def get_switch_status():
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    
    print("response",response)
    if ((len(response) > 12) and (response[6] == 0x12) and (response[7] == 0x06)):
        for loop_index in response:
            if (response[SWITCH_STATE_BYTE] == 0x01):
                device_state = 'on'
                button_id = response[SWITCH_ID_BYTE]
                device_group = response[9]
                device_zone = response[8]
                write_device_state_db(device_group,device_zone, button_id, device_state)
                print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
                return 'on'
            else:
                device_state='off'
                button_id = response[SWITCH_ID_BYTE]
                device_group = response[9]
                device_zone = response[8]
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
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_zone,device_group,button_id,device_state_l,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_zone,device_group,button_id,device_state_l,device_state_h,crc8,0x03]
    v_send_request_status = bytearray(send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    print("response set_switch_state ",response)
    response = 0

######################################

    
############################################################################
# Curtain 
############################################################################
def get_curtain_status():
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    
    print("response",response)
    if ((len(response) > 12) and (response[6] == 0x13) and (response[7] == 0x06)):
        for loop_index in response:
            device_state = response[12] #UP 0x01, Down or Stop 0x00
            button_id = response[8] # no need for this 
            device_group = response[10]
            device_zone = response[9]
            #write_device_state_db(device_group,device_zone, button_id, device_state)
        print("device_group",device_group,",device_zone", device_zone,",button_id,", button_id, ",device_state", device_state )
        response = 0
        
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
    print("response set_switch_state ",response)
    response = 0

############################################################################
# Sensors and Emergency
############################################################################

def get_emergency_status():
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
   

############################################################################
# Lists
############################################################################
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

############################################################################
# Database calls
############################################################################

def write_device_state_db(device_group,device_zone, button_id, device_state):
    setState(device_group,device_zone,button_id,device_state)
    return
######################################
def read_device_state_db(device_name,device_zone,device_group):
    return device_state

############################################################################

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
    print("%04X"%(Crc))
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
    Packet[6]=((Crc >>8)&0x00FF)
    Packet[7]=((Crc)&0x00FF)
    Socket.send(bytearray(Packet))
    print(bytearray(Packet))

def AirCond_StatusPacket(AirCond_ID,Socket):
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
    Socket.send(bytearray(Packet))
    print(bytearray(Packet))


def AirCond_SocketComm(portNo,Str_Ip,Socket):
    Socket.connect((Str_Ip, portNo))
    # receive Init Message from Sena Dummy Receive
    received = Socket.recv(1024)
    print("received",received) 
  
HOST = '192.168.1.100'
PORT = 7001
AirCond_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("AirCond_socket",AirCond_socket)
AirCond_SocketComm(PORT,HOST,AirCond_socket)

if __name__ == '__main__':
    token = Login(email,password)


#setState(3,1,9,'on')
while True:
    #device_group,device_zone, button_id
 
    get_switch_status()
    sleep(.1)
    GetState()

    set_curtain_state(0x01,0x01,0x01,'up')
    sleep(2)
    set_curtain_state(0x01,0x01,0x01,'stop')
    sleep(2)
    set_curtain_state(0x01,0x01,0x01,'down')
    sleep(2)
    get_curtain_status()
    

    AirCond_StatusPacket(0x01,AirCond_socket)
    Received_Packet = AirCond_socket.recv(1024)
    print("Received_Packet", Received_Packet)
     

    #print (groupList)
    #print (buttonList)
    #print (stateList)

    #set_switch_All(0x01, 0x03,'off')
    #set_switch_state(0x01, 0x03, 0x01, 'on')
    #get_emergency_status()
    sleep(2)

    
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