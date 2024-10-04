import can
import time
import ics
from enum import Enum
from Can_TP import send_one_frame, send_multi_frame, send_single_frame

class CAN_TYPE(Enum):
    CAN_2_0_MAX_PAYLOAD = 7 # 8 bytes for CAN 2.0
    CAN_FD_MAX_PAYLOAD = 64  # 64 bytes for CAN FD
 
def setup_virtual_can_bus():
    """Set up a virtual CAN bus interface."""
    return can.Bus(interface='virtual', channel=1, bitrate = 1000000, receive_own_messages = False)
 
 
def send_frame(bus, data, is_can_fd):
    if isinstance(data, str):
        data = bytearray(data, 'utf-8')
    data_length = len(data)
    max_payload = CAN_TYPE.CAN_FD_MAX_PAYLOAD.value if is_can_fd else CAN_TYPE.CAN_2_0_MAX_PAYLOAD.value
    # Kiểm tra độ dài dữ liệu và quyết định loại frame để gửi
    if data_length <= max_payload:
        # Gửi Single Frame
        send_single_frame(bus, data, is_can_fd = is_can_fd)
    else:
        # Gửi Multi Frame
        send_multi_frame(bus, data, is_can_fd = is_can_fd)
 

if __name__ == "__main__":
    # Use virtual or neovi based on preference
    use_virtual_bus = False
 
    if use_virtual_bus:
        bus = setup_virtual_can_bus()
    else:
        bus = can.Bus(interface='neovi', channel = 1, bitrate = 1000000, receive_own_messages = False)
 
    try:
        
        while True:
            user_input = input("Enter data to send (type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                print("Exiting...")
                break
            send_frame(bus, user_input.encode(), is_can_fd = True)  # Ensure data is in bytes
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()  # Safely shutdown the CAN bus