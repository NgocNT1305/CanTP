# Node_transmit.py

import can
import time
from Can_TP import can_tp_send

# Define message data
DATA = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

def setup_virtual_can_bus():
    # Use a virtual CAN interface for simulation
    return can.Bus(interface='virtual', channel = 1, bitrate = 1000000)

def send_data():
    try:
        # ics.GetDLLVersion()
        with can.Bus(interface='virtual', channel=1, bitrate = 1000000) as bus:
            while 1:
                msg = can.Message(arbitration_id=0x123, data=[0x11, 0x22, 0x33, 0x44], is_extended_id=False)
                bus.send(msg)
                print("Message sent successfully")
                # time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")
        # ics.find_devices()

if __name__ == "__main__":
    bus = setup_virtual_can_bus()
