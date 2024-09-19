#=========================================================================
# Can_TP.py
#=========================================================================
import can
import time
import ics
from enum import Enum

#Can type includes Can 2.0 and Can FD
class CAN_TYPE(Enum):
    CAN_2_0_MAX_PAYLOAD = 8  # 8 bytes for CAN 2.0
    CAN_FD_MAX_PAYLOAD = 64  # 64 bytes for CAN FD

# PCI types
class PCI_types(Enum):
    PCI_SF = 0x00  # Single Frame
    PCI_FF = 0x01  # First Frame
    PCI_CF = 0x02  # Consecutive Frame
    PCI_FC = 0x03  # Flow Control

class FS_types(Enum):
    FC_ERROR        = 0x00
    FC_OVERFLOW     = 0x01
    FC_WAIT         = 0x02
    FC_CONTINOUS    = 0x03

Check_arbitration_id = 0x123

def can_tp_send(data, is_can_fd=False):
    # CAN 2.0 payload is 8 bytes, CAN FD payload is 64 bytes
    max_payload = CAN_TYPE.CAN_FD_MAX_PAYLOAD.value if is_can_fd else CAN_TYPE.CAN_2_0_MAX_PAYLOAD.value
    frames = []
    data_length = len(data)

    # Calculate how many bytes can be used for data in a single frame
    if data_length <= max_payload - 1:
        # Single Frame (SF) - PCI byte takes up the first byte
        pci_byte = (PCI_types.PCI_SF.value << 4) | (data_length & 0x0F)
        frame = [pci_byte] + data
        frames.append(frame)
    else:
        # First Frame (FF) - Two bytes for PCI, rest for data
        first_frame_data_length = max_payload - 2
        pci_bytes = [(PCI_types.PCI_FF.value << 4) | ((data_length >> 8) & 0x0F), data_length & 0xFF]
        frame = pci_bytes + data[:first_frame_data_length]
        frames.append(frame)
        # Consecutive Frames (CF) - Sequence number starts at 1
        seq_num = 1
        for i in range(first_frame_data_length, data_length, max_payload - 1):
            pci_byte = (PCI_types.PCI_CF.value << 4) | (seq_num & 0x0F)
            frame = [pci_byte] + data[i:i + (max_payload - 1)]
            frames.append(frame)
            seq_num = (seq_num + 1) & 0x0F  # Sequence number wraps around at 0xF

    return frames

def receive_can_tp_messages(bus):
    received_frames = []
    full_message = bytearray()  # Buffer to store reassembled data
    expected_sequence_number = 1  # Sequence number for consecutive frames
    total_length = 0  # Total length of the message (from FF)

    while True:
        # Read a message from the bus
        msg = bus.recv(timeout=5)
        if msg:
            print(msg)
            #print("Timeout waiting for CAN message.")
        else:     
            print("No message received within the timeout period.")
            time.sleep(2)