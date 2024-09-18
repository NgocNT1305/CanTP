# Node_transmit.py

import can
import time
from Can_TP import can_tp_send

# Define message data
DATA = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]

def setup_virtual_can_bus():
    # Use a virtual CAN interface for simulation
    return can.Bus(interface='virtual', channel = 1, bitrate = 1000000)

def send_data(bus):
    #send data to the node receiver
    try:
        frames = can_tp_send(DATA, is_can_fd = False)
        for frame in frames:
            msg = can.Message(arbitration_id=0x123, data=frame, is_extended_id=False)
            bus.send(msg)
            print(f"Send Frame: {frame}")
            time.sleep(0.1)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    bus = setup_virtual_can_bus()
    print("Node is transmitting data ...")
    send_data(bus)
