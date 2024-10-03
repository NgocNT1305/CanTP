import can
import time
from Can_TP import receive_can_tp_messages
 
def setup_virtual_can_bus():
    return can.Bus(interface='virtual', channel=1, bitrate=1000000, receive_own_messages = False)
 
def setup_neovi_bus():
    return can.Bus(interface='neovi', channel=1, bitrate = 1000000, receive_own_messages = False)
 
def process_received_data(bus):
    """Process incoming CAN messages."""
    full_message = receive_can_tp_messages(bus)

    if full_message:
        # Làm phẳng danh sách nếu cần
        flattened_message = [byte for sublist in full_message for byte in (sublist if isinstance(sublist, list) else [sublist])]
        
        # Chuyển đổi byte thành chuỗi ký tự
        decoded_message = ''.join(chr(byte) for byte in flattened_message)
        
        # ANSI escape code để đổi màu đỏ cho tin nhắn
        red_color = "\033[34m"
        reset_color = "\033[0m"

        # In message với màu đỏ
        print(f"{red_color}Received message: {decoded_message}{reset_color}")
    else:
        # Mặc định không đổi màu cho phần này
        print("No frames received.")


if __name__ == "__main__":
    use_virtual_bus = True  # Set to True to use the virtual bus
 
    if use_virtual_bus:
        bus = setup_virtual_can_bus()
    else:
        bus = setup_neovi_bus()
 
    try:
        while True:
            print("Receive data from the bus")
            process_received_data(bus)
            time.sleep(0.1)  # Delay to prevent high CPU usage
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()