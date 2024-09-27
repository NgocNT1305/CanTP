# main.py
 
import threading
import subprocess
import Node_receiver
import Node_transmit
import time
 
 
def run_transmit():
    subprocess.run(["python", "Node_transmit.py"])
 
def run_receive():
    subprocess.run(["python", "Node_receiver.py"])
 
if __name__ == "__main__":
 
    try:
        bus = Node_transmit.setup_virtual_can_bus()
        user_input = input("Enter data to send: ")
        Node_transmit.send_frame(bus, user_input)
        Node_receiver.process_received_data(bus)
        time.sleep(0.1)
    finally:
        bus.shutdown()