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

base_url = 'http://localhost:9001'
token =''
email='root@root.com'
password='123456789'
idList=[]
TargetList=[]
CurrentList=[]
powerList=[]
modeList=[]
fanList=[]

def ChkState_inLists(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    print(idd,power,mode,Ttemp,Ctemp,fanSpeed)
    for i in range(len(idList)):
        if idList[i] == idd :
            if modeList[i]==mode and powerList[i]==power and TargetList[i]==Ttemp and CurrentList[i]==Ctemp and fanList[i]==fanSpeed:
                return True
    return False
def setState_inLists(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    for i in range(len(idList)):
        if idList[i] == idd :
            powerList[i]=power
            modeList[i]=mode
            TargetList[i]=Ttemp
            CurrentList[i]=Ctemp
            fanList[i]=fanSpeed
            powerList[i]=power

def Chk_inLists(idd,power,mode,Ttemp,Ctemp,fanSpeed):
    for i in range(len(idList)):
        if idList[i] == idd:
                return True
    return False

def Login(email,password):
    data ={'email': email, 'password': password}
    url = base_url+'/auth/local/'
    headers = {'Accept': 'application/json'}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url,data=data)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        return loaded_json['token']

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
    print ('Values => ',idd,power,mode,Ttemp,Ctemp,fanSpeed)
    id = GetTargetAC(idd)
    print (id)
    if id !=None:
        ac_body = {'_id':id ,'currentTemp':Ctemp ,'targetTemp': Ttemp,'fanSpeed': fanSpeed,'mode': mode,'value': power,'macAddress': None,'tag': None,'version':None,'intensity': None,'group': None,'zone': None,'__v': '','name': '','email': '','picture': '','createdBy': ''}
        url = base_url+'/api/v1/acs/'+id
        header = { 'Authorization': 'Bearer '+token}
        response = requests.put(url,headers=header,data=ac_body)
        if(response.status_code==200):
            return 'ok'
    else:
        CreateAC((str(id)+'_'),idd,power,mode,Ttemp,Ctemp,fanSpeed)

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
                
def GetACValues(id):
    url = base_url+'/api/v1/acs/'
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+str(token),'Accept-Language': 'en_US'}
    # call get service with headers and params
    response = requests.get(url,headers=header)
    if(response.status_code==200):
        loaded_json = json.loads(response.text)
        for item in loaded_json:
            try:
                if  item['group']==id :
                    return [item['value'],item['mode'] ,item['currentTemp'] ,item['targetTemp'] ,item['fanSpeed'] ]
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
    Packet[7]=((Crc >>8)&0x00FF)
    Packet[6]=((Crc)&0x00FF)
    Socket.send(bytearray(Packet))
    print("sent ",bytearray(Packet))
    sleep(.3)
    received = Socket.recv(1024)
    print("received",received) 

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
        
    if Chk_inLists(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
        idList.append(AC_ID)
        powerList.append(state)
        modeList.append(mode)
        TargetList.append(AC_TargetTemp)
        CurrentList.append(AC_CurrentTemp)
        fanList.append(AC_Fan)
    else:
        if ChkState_inLists(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
            setState_inLists(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)
            setACValues(AC_ID,state,mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)
            print(AC_ID,AC_Status,AC_CurrentTemp,AC_TargetTemp ,AC_Mode,AC_Fan)
##################################################
def read_AC_state_db():

    valuesList=GetACValues(1)
    AC_ID=1
    AC_Status=valuesList[0]
    AC_CurrentTemp=valuesList[2]
    AC_TargetTemp=valuesList[3]
    AC_Mode=valuesList[1]
    AC_Fan= valuesList[4]
    #idd,power,mode,Ttemp,Ctemp,fanSpeed)
    if Chk_inLists(AC_ID,AC_Status,AC_Mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
        idList.append(AC_ID)
        powerList.append(AC_Status)
        modeList.append(AC_Mode)
        TargetList.append(AC_TargetTemp)
        CurrentList.append(AC_CurrentTemp)
        fanList.append(AC_Fan)
    else:
        if ChkState_inLists(AC_ID,AC_Status,AC_Mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)==False:
            setState_inLists(AC_ID,AC_Status,AC_Mode,AC_TargetTemp,AC_CurrentTemp,AC_Fan)
            #AC_Status
            if(AC_Status == 'on'):
              AirCond_WriteControlPacket(AC_ID ,0x00 ,0x01 ,AirCond_socket)  
            elif(AC_Status == 'off'):
              AirCond_WriteControlPacket(AC_ID ,0x00 ,0x00 ,AirCond_socket)

            #AC_TargetTemp
            AirCond_WriteControlPacket(AC_ID ,0x02 , AC_TargetTemp ,AirCond_socket)
            
            #AC_Mode
            if(AC_Mode == 'cool'):
              AirCond_WriteControlPacket(AC_ID ,0x03 ,0x01 ,AirCond_socket)  
            elif(AC_Mode == 'fan'):
              AirCond_WriteControlPacket(AC_ID ,0x03 ,0x00 ,AirCond_socket)
            elif(AC_Mode == 'heat'):
              AirCond_WriteControlPacket(AC_ID ,0x03 ,0x02 ,AirCond_socket)
              
            #AC_Fan
            AirCond_WriteControlPacket(AC_ID ,0x04 , AC_Fan ,AirCond_socket)
      
##################################################

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
    while True:

        AirCond_StatusPacket(0x01,AirCond_socket)
        AirCond_GetStatusPacket(AirCond_socket.recv(1024))
        read_AC_state_db()
        
        print(idList)
        print(powerList)
        print(modeList)
        print(TargetList)
        print(CurrentList)
        print(fanList)
        sleep(5)
