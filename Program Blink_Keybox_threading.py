import can
import time
import threading

global busActive
global current_node_id
global bus
global current_bitrate
global shutdown

shutdown = False
busActive = False
current_bitrate = 125000 
#current_bitrate = 1000000 # Delete Me for new production

target_bitrate = 0x00 # 0x00 = 1mb, 0x02 = 500k, 0x03 = 250k, 0x04 = 125k

current_node_id = 0x0C 
#current_node_id = 0x53  # Delete Me for new production

target_node_id = 0x53
active_on_startup = 0x01 # 0x01 = Active, 0x00 = Inactive...
bootup_message = 0x01 # 0x01 = Active, 0x00 = Inactive...
periodic_fault_tx_ms = 1000 # 0-65535 ms
consumer_hbeat_id = 0x52 # consumer heartbeat node ID (0x700+ Node ID)
consumer_hbeat_time = 5000 # consumer heartbeat time ms..


bus = can.ThreadSafeBus(interface='pcan', channel='PCAN_USBBUS1', bitrate=current_bitrate)
busActive = True
msg = can.Message(arbitration_id=0x000, data=[0x01,0x00], is_extended_id=False)
bus.send(msg)
def setup_and_read_device():
    global current_bitrate
    global current_node_id
    global bus
    global busActive
    # set device active on startup
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x2F,0x13,0x20,0x00,active_on_startup,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Sent set device active on startup")
    time.sleep(0.02)

    # read device active on startup
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x40,0x13,0x20,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Request result set device active on startup")
    time.sleep(0.02)


    # request bootup message Active on startup
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x2F,0x15,0x20,0x00,bootup_message,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Sent set Bootup active on startup")
    time.sleep(0.02)

    # read bootup message active on startup
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x40,0x15,0x20,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Request result set device active on startup")
    time.sleep(0.02)


    # Set Periodic Fault Transmission to 1000 ms.
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x2B,0x12,0x20,0x00,(periodic_fault_tx_ms & 0xFF),((periodic_fault_tx_ms>>8) & 0xFF),0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Sent set Fault time tx ms value")
    time.sleep(0.02)

    # read Periodic Fault Transmission 
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x40,0x12,0x20,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Request result Fault time  txms")
    time.sleep(0.02)

    
    # Set Consumer Heartbeat to 5000ms and node 0x52.
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x23,0x16,0x10,0x01,(consumer_hbeat_time & 0xFF),((consumer_hbeat_time >> 8) & 0xFF),consumer_hbeat_id,0x00], is_extended_id=False)
    bus.send(msg)
    print("Sent Set Consumer Heartbeat and ID.")
    time.sleep(0.02)

    # read Consumer Heartbeat info 
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x40,0x16,0x10,0x01,0x00,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Request Consumer heartbeat info..")
    time.sleep(0.02)

    # Set Node ID
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x2F,0x11,0x20,0x00,target_node_id,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Sent Set Node ID")
    current_node_id = target_node_id
    time.sleep(0.02)

    # read Node ID
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x40,0x11,0x20,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Request Node ID")
    time.sleep(0.02)


    # Set Bitrate to target bitrate
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x2F,0x10,0x20,0x00,target_bitrate,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    busActive = False
    bus.shutdown()
    print("Sent Set Bitrate")
    if target_bitrate == 0x00:
        current_bitrate = 1000000
    if target_bitrate == 0x02:
        current_bitrate = 500000
    if target_bitrate == 0x03:
        current_bitrate = 250000
    if target_bitrate == 0x04:
        current_bitrate = 125000
    time.sleep(1)
    bus = can.ThreadSafeBus(interface='pcan', channel='PCAN_USBBUS1', bitrate=current_bitrate)
    busActive = True
    time.sleep(0.02)


    # read bitrate
    msg = can.Message(arbitration_id=(0x600+current_node_id), data=[0x40,0x10,0x20,0x00,0x00,0x00,0x00,0x00], is_extended_id=False)
    bus.send(msg)
    print("Request Bitrate")
    time.sleep(0.02)

    print("Process Completed")
    shutdown = True
    time.sleep(1)
    exit()



def monitor_bus():
    global current_node_id
    global shutdown
    while shutdown == False:
        try:
            if busActive == True:
                for msg in bus:
                    if msg.arbitration_id == 0x580+current_node_id:
                        #print(msg)
                        if msg.data[0] == 0x4F:
                            if (msg.data[2] == 0x20) and (msg.data[1] == 0x13):
                                if msg.data[4] == 0x01:
                                    print("Device active on startup")
                                elif msg.data[4] == 0x00:
                                    print("Device inactive on startup")
                                else:
                                    print("Unknown Value for COB ID 0x1320")

                            elif (msg.data[2] == 0x20) and (msg.data[1] == 0x15):
                                if msg.data[4] == 0x01:
                                    print("Bootup Message active on startup")
                                elif msg.data[4] == 0x00:
                                    print("Bootup Message inactive on startup")
                                else:
                                    print("Unknown Value for COB ID 0x1520")
                            
                            elif (msg.data[2] == 0x20) and (msg.data[1] == 0x10):
                                if msg.data[4] == 0x00:
                                    print("Bitrate 1M")
                                elif msg.data[4] == 0x02:
                                    print("Bitrate 500k")
                                elif msg.data[4] == 0x03:
                                    print("Bitrate 250k")
                                elif msg.data[4] == 0x04:
                                    print("Bitrate 125k")
                                else:
                                    print("Unknown Value for COB ID 0x1020")
                            
                            elif (msg.data[2] == 0x20) and (msg.data[1] == 0x11):
                                recvnodeID = msg.data[4]
                                print ("node id is now 0x%02X "% (recvnodeID))

                            

                        elif msg.data[0] == 0x4B:
                            if (msg.data[2] == 0x20) and (msg.data[1] == 0x12):
                                msvalue = (msg.data[5]<<8) + msg.data[4] 
                                print("Fault ms %i value" % (msvalue))

                        elif msg.data[0] == 0x43:
                            if (msg.data[2] == 0x10) and (msg.data[1] == 0x16):
                                if msg.data[3] == 0x01:
                                    msval = int((msg.data[5]<<8) + msg.data[4])
                                    nodeidresp = msg.data[6]
                                    print(" heart beat node ID 0x%02x at %i ms" % (nodeidresp, msval))
                        


                        elif msg.data[0] == 0x60:
                            print("message acknowledged")

        #            else:
        #                print("message received... ")
        #                print(msg)
        except:
            pass

# Creating threads
thread1 = threading.Thread(target=setup_and_read_device)
thread2 = threading.Thread(target=monitor_bus)

# Starting threads
thread1.start()
thread2.start()

# Joining threads to the main thread
thread1.join()
thread2.join()