# main.py

import threading
import subprocess
import Node_receiver
import Node_transmit
import time
# Define the functions to run each script
def run_transmit():
    subprocess.run(["python", "Node_transmit.py"])

def run_receive():
    subprocess.run(["python", "Node_receiver.py"])

if __name__ == "__main__":

    try:
        bus = Node_transmit.setup_virtual_can_bus()
        print("Node is transmitting data ...")
        Node_transmit.send_data(bus)
        Node_receiver.process_received_data(bus)
        time.sleep(2)
    finally:
        bus.shutdown()
