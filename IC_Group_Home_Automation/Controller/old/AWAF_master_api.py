# Import socket module
import socket			
from time import sleep



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
    Packet[6]=((Crc >>8)&0x00FF)
    Packet[7]=((Crc)&0x00FF)
    Socket.send(bytearray(Packet))



def AirCond_SocketComm(portNo,Str_Ip,Socket):
    
    Socket.connect((Str_Ip, portNo))
    # receive Init Message from Sena Dummy Receive
    Socket.recv(1024) 
    



AirCond_socket = socket.socket()
AirCond_SocketComm(7001,'192.168.1.100',AirCond_socket)	

	
while True:
     AirCond_StatusPacket(0x01,AirCond_socket)
     Received_Packet=AirCond_socket.recv(1024)
    
    

