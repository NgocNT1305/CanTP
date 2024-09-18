import can
from Can_TP import receive_can_tp_messages

def setup_virtual_can_bus():
    # Use a virtual CAN interface for simulation
    return can.Bus(interface='virtual', channel=0, bitrate=1000000)

def process_received_data(bus):
    # Receive CAN TP messages using the Can_TP module
    received_frames = receive_can_tp_messages(bus)
    
    if received_frames:
        # Concatenate the data from all frames into one bytearray
        full_message = bytearray()
        
        # Iterate through received frames
        for frame in received_frames:
            # Extract the frame's data and append it to full_message
            full_message.extend(frame.data[1:])  # Skip the PCI byte

        try:
            # Decode the received bytearray as UTF-8 string
            print(f"Full received message: {full_message.decode('utf-8')}")
        except UnicodeDecodeError:
            print("Received non-text data.")

if __name__ == "__main__":
    bus = setup_virtual_can_bus()
    process_received_data(bus)
