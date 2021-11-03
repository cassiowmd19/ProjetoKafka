#!/user/bin/env python3
import time

from kafka import KafkaProducer
import paho.mqtt.client as mqtt

import socket
import struct
import json

######################### FUNÇÕES MQTT ###############################

def on_connect(client, userdata, flags, rc):
    print("Connected - rc:", rc)


def on_message(client, userdata, message):
    global FLAG
    global chat
    if str(message.topic) != pubtop:
        msg = str(message.payload.decode("utf-8"))
        SetMsg(msg)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed:", str(mid), str(granted_qos))

def on_unsubscirbe(client, userdata, mid):
    print("Unsubscribed:", str(mid))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected Disconnection")

################################## CONEXÃO MQTT ########################################

host = socket.gethostname()
broker_address = host
port = 1883
client = mqtt.Client()
client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscirbe
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port)

pubtop = "/Request/client"
subtop = "/Request/Adm"
FLAG = True
chat = None
msgm = None
request = None

client.loop_start()
client.subscribe(subtop)


##################### CONFIGURAÇÃO PRODUTOR KAFKA #######################

def serializer(message):
    return json.dumps(message).encode('utf-8')

producer = KafkaProducer(
    bootstrap_servers = ['localhost:9092'],
    value_serializer= serializer
)


########################### CONEXÃO VIA SOCKET COM CLIENTE #############################

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', MCAST_PORT))
mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
#4 bytes (4s) seguidos de um long (l), usando ordem nativa (=)

s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


def SetMsg(msg):
    global mensagem
    mensagem = msg

def GetMsg():
    return mensagem

def login(key, senha):
    text = str("Login" + "," + key + "," + senha)
    producer.send('messages', text)
    time.sleep(2)

SetMsg(None)

############################## INICIO SERVIDOR #######################################
while True:
    try:
        data, addr = s.recvfrom(1024)
        if (str(data.decode()).split(",") != [""]):
            funcao = str(data.decode()).split(",")[0]
            key = str(data.decode()).split(",")[1]
            senha = str(data.decode()).split(",")[2]
        else:
            funcao = None
            key = None
            senha = None


        if funcao == "login":
            login(key, senha)
            print("Conexão: ", addr)


        elif funcao == "InsereTarefa":
            idtarefa = str(data.decode()).split(",")[3]
            nometarefa = str(data.decode()).split(",")[4]
            text = str(funcao + "," + key + "," + idtarefa + "," + nometarefa)
            producer.send('messages', text)
            time.sleep(2)


        elif funcao == "AlteraTarefa":
            idtarefa = str(data.decode()).split(",")[3]
            nometarefa = str(data.decode()).split(",")[4]
            text = str(funcao + "," + key + "," + idtarefa + "," + nometarefa)
            producer.send('messages', text)
            time.sleep(2)


        elif funcao == "listaTarefa":
            text = str(funcao + "," + key)
            producer.send('messages', text)
            time.sleep(2)


        elif funcao == "buscaTarefaConcl":
            text = str(funcao + "," + key)
            producer.send('messages', text)
            time.sleep(2)


        elif funcao == "apagarTarefa":
            keyTarefa = str(data.decode()).split(",")[3]
            text = str(funcao + "," + key + "," + keyTarefa)
            producer.send('messages', text)
            time.sleep(2)


        elif funcao == "concluirTarefa":
            keyTarefa = str(data.decode()).split(",")[3]
            text = str(funcao + "," + key + "," + keyTarefa)
            producer.send('messages', text)
            time.sleep(2)

    except ConnectionRefusedError:
        print("Encerrada conexão com cliente %s" % addr)

    if GetMsg() != None:
        s.sendto(GetMsg().encode(), addr)

client.disconnect()
client.loop_stop()
conn.close()  # Close the connection
