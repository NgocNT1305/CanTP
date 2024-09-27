import can
import time
import ics
from Can_TP import send_single_frame, send_multi_frame
 
def setup_virtual_can_bus():
    """Set up a virtual CAN bus interface."""
    return can.Bus(interface='virtual', channel=1, bitrate=1000000, receive_own_messages = False)
 
 
def send_frame(bus, data, is_can_fd = False):
    if isinstance(data, str):
        data = bytearray(data, 'utf-8')
    data_length = len(data)
    if data_length <= 7:
        send_single_frame(bus, data, is_can_fd = False)
    else:
        send_multi_frame(bus, data, is_can_fd = False)
 
 
if __name__ == "__main__":
    # Use virtual or neovi based on preference
    use_virtual_bus = False
 
    if use_virtual_bus:
        bus = setup_virtual_can_bus()
    else:
        bus = can.Bus(interface='neovi', channel=1, bitrate = 1000000, receive_own_messages = False)
 
    try:
        
        while True:
            user_input = input("Enter data to send (type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                print("Exiting...")
                break
            send_frame(bus, user_input.encode(), is_can_fd = False)  # Ensure data is in bytes
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()  # Safely shutdown the CAN bus