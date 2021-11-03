import json

from kafka import KafkaConsumer
from funcaoserver import FuncaoServer
from administrador.hashtable import HashTable

import paho.mqtt.client as mqtt
import socket

############################## FUNÇÕES MQTT ##############################


def on_connect(client, userdata, flags, rc):
    print("Connected - rc:", rc)

def on_message(client, userdata, message):
    global FLAG
    global chat
    if str(message.topic) != pubtop:
        msg = str(message.payload.decode("utf-8"))
        SetMsg(msg)
        print("Retorno: ", msg)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed:", str(mid), str(granted_qos))

def on_unsubscirbe(client,userdata,mid):
    print("Unsubscribed:", str(mid))

def on_disconnect(client,userdata,rc):
    if rc !=0:
        print("Unexpected Disconnection")


########################## CRIANDO CONEXÃO MQTT ########################

host = socket.gethostname()
broker_address = host
port = 1883

client = mqtt.Client()
client.on_subscribe = on_subscribe
client.on_unsubscribe = on_unsubscirbe
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, port)

pubtop = "/Request/Adm"
subtop = "/Request/client"

client.subscribe(subtop)

client.loop_start()
client.subscribe(subtop)
FLAG = True
chat = None

def SetMsg(msg):
    global mensagem
    mensagem = msg

def GetMsg():
    return mensagem

func = FuncaoServer()
hash = HashTable()


######################### INSERE PRIMEIRO ADM ###########################

hash = HashTable()
dados = ["nome", "senha"]
key = "01"
hash.insert(key, dados)


if __name__ == '__main__':
    consumer = KafkaConsumer(
        'messages',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='earliest'
    )

    for message in consumer:
            msgm = str(json.loads(message.value))
            if msgm is not None:
                try:
                    funcao = msgm.split(",")[0]
                    key = msgm.split(",")[1]
                except:
                    funcao = ""
                    key = ""

                if funcao == "InsereCliente":
                    nome = msgm.split(",")[2]
                    senha = msgm.split(",")[3]
                    msg = func.InsereCliente(key, nome, senha)
                    print("InsereCliente -> Return ", funcao)
                    client.publish(pubtop, msg)


                elif funcao == "AlteraCliente":
                    nome = msgm.split(",")[2]
                    senha = msgm.split(",")[3]
                    msg = func.AlteraCliente(key, nome, senha)
                    client.publish(pubtop, msg)
                    print("AlteraCliente -> Return ", msg)


                elif funcao == "BuscaCliente":
                    msg = func.BuscaCliente(key)
                    print("BuscaCliente -> Return ", msg)
                    client.publish(pubtop, str(msg))


                elif funcao == "ApagarCliente":
                    msg = func.ApagarCliente(key)
                    print("ApagarCliente -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "RemoveTarefa":
                    keytarefa = msgm.split(",")[2]
                    msg = func.ApagarTarefa(key, keytarefa)
                    print("RemoveTarefa -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "InsereTarefa":
                    keytarefa = msgm.split(",")[2]
                    nomeTarefa = msgm.split(",")[3]
                    print(msgm)
                    msg = func.InsereTarefa(key, keytarefa, nomeTarefa)
                    print("InsereTaref -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "AlteraTarefa":
                    keytarefa = msgm.split(",")[2]
                    nomeTarefa = msgm.split(",")[3]
                    msg = func.AlteraTarefa(key, keytarefa, nomeTarefa)
                    print("AlteraTarefa -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "BuscaTarefa":
                    keytarefa = msgm.split(",")[2]
                    msg = func.BuscaTarefa(key, keytarefa)
                    print("BuscaTarefa -> Return ", str(msg))
                    client.publish(pubtop, str(msg))


                elif funcao == "InsereAdm":
                    nome = msgm.split(",")[2]
                    senha = msgm.split(",")[3]
                    msg = hash.insert(key,[nome,senha])
                    print("InsereAdm -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "AlteraAdm":
                    nome = msgm.split(",")[2]
                    senha = msgm.split(",")[3]

                    nn = hash.setnome(key, nome)
                    ns = hash.setsenha(key, senha)

                    if nn != nome:
                        client.publish(pubtop, nn)
                    elif ns != senha:
                        client.publish(pubtop, ns)
                    else:
                        client.publish(pubtop, True)


                elif funcao == "listaTarefa":
                    msg = func.ListaTarefa(key)
                    print("listaTarefa -> Return Lista")
                    client.publish(pubtop, str(msg))


                elif funcao == "buscaTarefaConcl":
                    msg = func.ListaTarefaConcluidas(key)
                    print("buscaTarefaConcl -> Return Lista")
                    client.publish(pubtop, str(msg))


                elif funcao == "apagarTarefa":
                    keyTarefa = msgm.split(",")[2]
                    msg = func.ApagarTarefa(key, keyTarefa)
                    print("apagarTarefa -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "concluirTarefa":
                    keyTarefa = msgm.split(",")[2]
                    msg = func.ConcluirTarefa(key, keyTarefa)
                    print("concluirTarefa -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "LoginAdm":
                    senha = msgm.split(",")[2]
                    msg = hash.validaSenha(key, senha)
                    print("LoginAdm -> Return ", msg)
                    client.publish(pubtop, msg)


                elif funcao == "Login":
                    senha = msgm.split(",")[2]
                    msg = func.Login(key, senha)
                    print("LoginCliente -> Return ", msg)
                    client.publish(pubtop, msg)
