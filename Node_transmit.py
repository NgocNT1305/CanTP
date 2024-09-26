import can
import time
import ics
from enum import Enum

class CAN_TYPE(Enum):
    CAN_2_0_MAX_PAYLOAD = 8  # 8 bytes for CAN 2.0
    CAN_FD_MAX_PAYLOAD = 64  # 64 bytes for CAN FD
from Can_TP import send_single_frame, send_multi_frame

def setup_virtual_can_bus():
    """Set up a virtual CAN bus interface."""
    return can.Bus(interface='virtual', channel=1, bitrate=1000000, receive_own_messages = False)

def send_data(bus, data):
    """Send data frames over the CAN bus."""
    if isinstance(data, str):
        data = bytearray(data, 'utf-8')

    if len(data) <= CAN_TYPE.CAN_2_0_MAX_PAYLOAD.value - 1:
        send_single_frame(bus, data)
    else:
        send_multi_frame(bus, data)


if __name__ == "__main__":
    # Use virtual or neovi based on preference
    use_virtual_bus = False
 
    if use_virtual_bus:
        bus = setup_virtual_can_bus()
    else:
        bus = can.Bus(interface='neovi', channel=1, bitrate=1000000)
 
    try:
        
        while True:
            user_input = input("Enter data to send (type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                print("Exiting...")
                break
            send_data(bus, user_input.encode())  # Ensure data is in bytes
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()  # Safely shutdown the CAN bus
