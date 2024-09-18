# Node_receiver.py

import can
from Can_TP import receive_can_tp_messages

def setup_virtual_can_bus():
    # Use a virtual CAN interface for simulation
    return can.Bus(interface='virtual', channel=0, bitrate=1000000)

def process_received_data(bus):
    received_frames = receive_can_tp_messages(bus)
    if received_frames:
        # Concatenate frames
        data_received = b''.join([bytes(frame) for frame in received_frames])
        # Remove PCI bytes (if needed)
        # Example: Skip the first byte if it's a PCI byte
        data_received = data_received[1:]
        print(f"Received data: {data_received.decode('utf-8')}")

if __name__ == "__main__":
    bus = setup_virtual_can_bus()
    process_received_data(bus)
