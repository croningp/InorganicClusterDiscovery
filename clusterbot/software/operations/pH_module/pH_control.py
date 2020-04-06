"""
.. module:: pH_control
    :platform: Unix, Windows
    :synopsis: Module for controlling DrDAQ pH module in the base layer

.. moduleauthor:: Graham Keenan <https://github.com/ShinRa26>

"""

import os
import sys
import time
import socket
import inspect
import numpy as np

HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
root_path = os.path.join(HERE, "..", "..")
op_path = os.path.join(HERE, "..")
sys.path.append(op_path)
sys.path.append(root_path)

from base_layer.pH_module.DrDAQ import drDAQ

KILL_COMMAND = "KILL"


def run_server():
    pH = drDAQ()
    pH.set_rgb(255,0,0)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = ("127.0.0.1", 9000)
    try:
        server.bind(conn)
    except OSError as err:
        pH.set_rgb(255,0,0)
        print("Unable to start server: {}".format(err))

    server.listen(1)
    print("pH DrDAQ Server online!")
    pH.set_rgb(0,255,0)
    while True:
        # Wait for a connection
        connection, client_address = server.accept()

        try:
            print ('Connection from', client_address)


            data = connection.recv(16)
            if data.decode() == KILL_COMMAND:
                pH.set_rgb(255,0,0)
                break
            # print >>sys.stderr, 'received "%s"' % data
        
            print ('Starting pH measurement') 

            try:
                print ('DrDAQ ready for measurement')
                pH.set_rgb(0,0,255)                
                pH.run_single_shot()
                pH.sampling_done()
                
                time.sleep(1.)
                pH.sampling_done()
                samples = pH.get_sampled_values()
                pH.stop_sampling()
                pH.set_rgb(0,255, 0)
                # drDAQ.close_unit()                                                                                   
                                                                                        
            except:
                print ('Error Opening Picoscope')
                                    
            # print 'Creating pH dataFile' 
            # np.save('data.txt', samples)
        
            # print np.shape(samples)


            # estimating average pH and deviation
            pHvalue, stdev = np.mean(samples), np.std(samples)

            print ('Mean pH: ', pHvalue)
            print ('Standard Deviation: ', stdev) 
        
            print ('sending pH values back')
            connection.sendall(str(pHvalue).encode())

        except Exception as e:
            print("Error: {}".format(e))
            pH.set_rgb(255,0,0)
            break

        finally:    
            # clean up the connection
            connection.close()
                                   