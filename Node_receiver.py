import can
import ics
import time
from Can_TP import receive_can_tp_messages

# Global list to store data from received CAN TP frames
received_data_list = []

def setup_virtual_can_bus():
    # Use a virtual CAN interface for simulation
    return can.Bus(interface='virtual', channel = 1, bitrate = 1000000, receive_own_messages = True)

def process_received_data(bus):
    global received_data_list  # Declare the global variable

    # Receive CAN TP messages using the Can_TP module
    received_frames = receive_can_tp_messages(bus)

    if received_frames:
        full_message = bytearray()
        
        # Iterate through received frames
        for frame in received_frames:
            # Extract the frame's data and append it to full_message
            full_message.extend(frame.data[1:])  # Skip the PCI byte

            # Append the received frame data to the global list
            received_data_list.append(frame.data[1:])

        # Print the global list of received data
        print("Received Data List (from all frames):", received_data_list)

        try:
            # Decode the received bytearray as UTF-8 string
            print(f"Full received message: {full_message.decode('utf-8')}")
        except UnicodeDecodeError:
            print("Received non-text data.")

# if __name__ == "__main__":
#     try:
#         bus = setup_virtual_can_bus()
#         process_received_data(bus)
#     finally:
#         bus.shutdown()  # Đảm bảo bus được tắt


