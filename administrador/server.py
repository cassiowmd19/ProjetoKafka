# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Python implementation of the GRPC helloworld.Greeter server."""

from concurrent import futures

from hashtable import HashTable
from kafka import KafkaProducer
import paho.mqtt.client as mqtt
import logging

import grpc
import administrador_pb2
import administrador_pb2_grpc

import json
import time
import socket
host = socket.gethostname()


pubtop = "/Request/Adm"
subtop = "/Request/client"

FLAG = True
chat = None

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

def SetMsg(msg):
    global mensagem
    mensagem = msg

def GetMsg():
    return mensagem


class HelloServiceStub(administrador_pb2_grpc.HelloService):

    def Hello(self, request, context):
      try:
        funcao = request.funcao
        id = request.id
        senha = request.senha
        nome = request.nome
        idtarefa = request.idtarefa
        nometarefa = request.nometarefa
        idcliente = request.idcliente
        nomecliente = request.nomecliente
        senhacliente = request. senhacliente

        SetMsg(None)

        if funcao == "InsereCliente":
            text = str(funcao+","+idcliente+","+nomecliente+","+senhacliente)
            producer.send('messages', text)

        elif funcao == "AlteraCliente":
            text = str(funcao + "," + idcliente + "," + nomecliente + "," + senhacliente)
            producer.send('messages', text)

        elif funcao == "BuscaCliente":
            text = str(funcao + "," + idcliente)
            producer.send('messages', text)

        elif funcao == "ApagarCliente":
            text = str(funcao + "," + idcliente)
            producer.send('messages', text)

        elif funcao == "RemoveTarefa":
            text = str(funcao + "," + idcliente + "," + idtarefa)
            producer.send('messages', text)

        elif funcao == "InsereTarefa":
            text = str(funcao + "," + idcliente + "," + idtarefa + "," + nometarefa)
            producer.send('messages', text)

        elif funcao == "AlteraTarefa":
            text = str(funcao + "," + id + "," + idtarefa + "," + nometarefa)
            producer.send('messages', text)

        elif funcao == "BuscaTarefa":
            text = str(funcao + "," + idcliente + "," + idtarefa)
            producer.send('messages', text)

        elif funcao == "InsereAdm":
            text = str(funcao + "," + id + "," + nome + "," + senha)
            producer.send('messages', text)

        elif funcao == "AlteraAdm":
            text = str(funcao + "," + id + "," + nome + "," + senha)
            producer.send('messages', text)


        elif funcao == "LoginAdm":
            text = str(funcao + "," + id + "," + senha)
            producer.send('messages', text)

        elif funcao == "BuscaCliente":
            return administrador_pb2.HelloResponse(mensagem='Nome: %s' % nome)
        time.sleep(1)
      except :
          print("FALHA NA CONEXÃO SERVER CLIENTE!!!")

      return administrador_pb2.HelloResponse(mensagem=GetMsg())


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    administrador_pb2_grpc.add_HelloServiceServicer_to_server(HelloServiceStub(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
