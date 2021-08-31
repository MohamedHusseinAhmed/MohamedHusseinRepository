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
import paho.mqtt.client as mqtt
import threading 
base_url = 'http://localhost:9000'
token =''
email='root@root.com'
password='123456789'
idList=[]
groupList=[]
zoneList=[]
buttonList=[]
stateList=[]

idCurtainList=[]
groupCurtainList=[]
zoneCurtainList=[]
buttonCurtainList=[]
stateCurtainList=[]
NUM_BYTES_SWITCH_DATA  = 16
SWITCH_STATE_BYTE      = 12
SWITCH_ID_BYTE         = 10
write=0;
read=0;

master_port = serial.Serial('/dev/ttyUSB0', 9600,timeout = 2) # Establish the connection on a specific port
sensors_port = serial.Serial('/dev/ttyUSB2', 9600,timeout = 2) # Establish the connection on a specific port

ports = serial.tools.list_ports.comports()

#for i in range (0, len(ports)):
    
   # if ports[i].hwid[12]=='1'and ports[i].hwid[13] == 'A' and ports[i].hwid[14]== '8' and ports[i].hwid[15] == '6':
   #     print("Sensors Port connected" , ports[i].hwid)
   #     print("",ports[i].device)# This is Device that's will be used to connect serial
   #     sensors_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port
   # print(ports[i].hwid)
    #if ports[i].hwid[12]=='0'and ports[i].hwid[13] == '6' and ports[i].hwid[14]== '7' and ports[i].hwid[15] == 'B':    
        #print("USB to Serial Connected" , ports[i].hwid)
        #print("",ports[i].device)# This is Device that's will be used to connect serial
        #master_port = serial.Serial(ports[i].device, 9600,timeout = 2) # Establish the connection on a specific port
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


# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("devices/#")
    
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
            if read==0:
                GetCurtainState(msg.payload)
            print ("receive => "+loaded_json['group'])
            print ("receive => "+loaded_json['zone'])
            print ("receive => "+loaded_json['button'])
            print ("receive => "+loaded_json['value'])
    except IndexError:
        print ('not found')
    except KeyError:
        print ('not found')

######################################

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
    print(group)
    print(zone)
    print(button)
    id = GetTargetDevice(group,zone,button)
    print (id)
    if id !=None:
        MQTT_MSG=json.dumps({'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': group,'zone': zone,'button': button,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''})
        client.publish("devices/"+id, payload=MQTT_MSG)
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
                
def GetState(body):
    loaded_json = json.loads(body)
    try:
        #print('zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
        if Chk_inLists((loaded_json['group']),(loaded_json['zone']),(loaded_json['button']))==False:
            idList.append((loaded_json['_id']))
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
        device_body = {'_id':id ,'createdAt':None ,'updatedAt': None,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': None,'zone': None,'button': None,'value': state,'__v': '','name': '','email': '','picture': '','createdBy': ''}
        client.publish("curtains/"+id, payload=device_body, qos=0, retain=False)
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
    loaded_json = json.loads(body)
    #print (loaded_json)
    for item in loaded_json:
        try:
            print('Curtain => zone : '+ str(item['zone']) +' group :' +str(item['group'])+' button : '+str(item['button']) + ' State : '+ item['value'] )
            if ChkCurtain_inLists(item['group'],item['zone'],item['button'])==False:
                idCurtainList.append(item['_id'])
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
    if write==0:
        read=1
        response = master_port.read(13)
        master_port.flush()
        read=0
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
    write=1
    print("rx_zone ", device_zone)
    print("rx_group ",device_group)
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_group,device_zone,button_id,device_state_l,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x08,0x00,0x0A,0x12,0x03,device_group,device_zone,button_id,device_state_l,device_state_h,crc8,0x03]
    v_send_request_status = bytearray(send_request_status)
    print("sent set_switch_state ",v_send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    master_port.flush()
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    print("response set_switch_state ",response)
    response = 0
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
            #write_curtain_state_db(device_group,device_zone, button_id, device_state)
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
    write=1    
    crc8 = libscrc.intel(bytearray([0x02,0xE1,0x01,0x07,0x00,0x0A,0x13,0x03,button_id,device_zone,device_group,device_state_h]))
    send_request_status = [0x02,0xE1,0x01,0x07,0x00,0x0A,0x13,0x03,button_id,device_zone,device_group,device_state_h,crc8,0x03]
    v_send_request_status = bytearray(send_request_status)
    
    master_port.write(serial.to_bytes(v_send_request_status))
    response = 0
    response = master_port.read(NUM_BYTES_SWITCH_DATA)
    print("response set_curtain_state ",response)
    response = 0
    write=0

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
    setState(device_zone,device_group,button_id,device_state)
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

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")

######################################
    
if __name__ == '__main__':
    token = Login(email,password)
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.connect("localhost", 1883, 30)
    client.loop_forever()
    #x = threading.Thread(target=thread_function)
    #x.start()
    #setState(3,1,9,'on')
    while True:
        #device_group,device_zone, button_id
        #get_master_status()
        print (groupList)
        print (zoneList)
        print (buttonList)
        print (stateList)
        sleep(.2)
    