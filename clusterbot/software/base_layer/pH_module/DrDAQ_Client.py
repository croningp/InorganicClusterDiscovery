# ---------------------------------------------------------------- #
# ------ pH MEASUREMENT USING DR-DAQ ON RASPBERRY PI SERVER ------ #
# ---------------------------------------------------------------- #

# Abhishek Sharma
# Cronin Lab
# University of Glasgow
# abhishek.sharma@glasgow.ac.uk


"""
      Connects to Raspberry Pi server and gets back pH value from
      DrDAQ. To test:

      python pH_DrDAQ_client.py

"""


import sys
import socket

def receive_pH():
      """
      Connects to the DrDaq serverand receives the pH value

      Returns:
            data (str): pH value measured
      """
      # Create a TCP/IP socket
      socketClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      # Connect the socket to the port where the server is listening
      server_address = ('127.0.0.1', 9000)
      print("Connecting to server: {0} on port {1}".format(server_address[0], server_address[1]))
      socketClient.connect(server_address)

      message = 'measure pH value'
      print("Sending message: {0}".format(message))
      socketClient.sendall(message.encode())

      data = socketClient.recv(6)

      print('pH value : received: {0}'.format(data.decode()))

      socketClient.close()

      return data.decode("utf-8")

def kill_server():
      client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      addr = ("127.0.0.1", 9000)
      client.connect(addr)
      client.sendall("KILL".encode())
