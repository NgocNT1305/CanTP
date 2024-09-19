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

MAX_BLOCK_SIZE = 2

class FS_types(Enum):
    FC_ERROR        = 0x00
    FC_OVERFLOW     = 0x01
    FC_WAIT         = 0x02
    FC_CONTINOUS    = 0x03

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
    full_message = bytearray()
    
    while True:
        # Read a message from the bus
        msg = bus.recv(timeout=5)  # Increase timeout if needed
        
        if msg:
            pci_byte = msg.data[0] >> 4  # Lấy 4 bit cao để xác định loại PCI

            # Handle Single Frame (SF)
            if pci_byte == PCI_types.PCI_SF.value:
                SF_datalength = msg.data[0] & 0x0F  # Lấy 4 bit thấp để xác định độ dài dữ liệu
                received_frames.append(msg.data[1:1 + SF_datalength])  # Lấy dữ liệu từ byte 1 trở đi
                print(f"Single Frame received: {received_frames}, Data length: {SF_datalength}")

            # Handle First Frame (FF)
            elif pci_byte == PCI_types.PCI_FF.value:
                # Trường hợp data length <= 4095 byte
                if (msg.data[0] & 0x0F) < 0x0F:
                    # Chỉ lấy 4 bit cuối của byte đầu tiên và kết hợp với byte thứ hai
                    data_length = ((msg.data[0] & 0x0F) << 8) | msg.data[1]
                    data = list(msg.data[2:])
                    received_frames.append(data)  # Lấy dữ liệu từ byte 2 trở đi
                    print(f"First Frame data received (<= 4095): {data}, Data length: {data_length}")
                
                # Trường hợp data length > 4095 byte
                else:
                    # Tính toán data_length từ 4 byte tiếp theo (byte 1 đến byte 4)
                    data_length = ((msg.data[1] << 24) | (msg.data[2] << 16) | (msg.data[3] << 8) | msg.data[4])
                    # Lấy dữ liệu từ byte thứ 5 trở đi
                    data = list(msg.data[5:])  
                    print(f"First Frame data received (> 4095): {data}, Data length: {data_length}")
                
                block_size = MAX_BLOCK_SIZE
                send_flow_control(bus, FS_types.FC_CONTINOUS.value, block_size)

            elif pci_byte == PCI_types.PCI_CF.value:
                data = list(msg.data[1:])
                received_frames.append(data)
                print(f"Consecutive Frame data received: {data}")
            
            if sum(len(frame) for frame in received_frames) >= data_length:
                print(f"All frames received. Total data length: {data_length}")
                break  # Kết thúc khi nhận đủ dữ liệu

    return received_frames

#==========================================================================

def send_flow_control(bus, fs=FS_types.FC_CONTINOUS.value, block_size=15, st_min=0):
    # Chuẩn bị dữ liệu cho Flow Control frame
    # FS (Flow Status) là byte đầu tiên, BS (Block Size) là byte thứ hai, STmin là byte thứ ba
    fc_frame_data = [fs, block_size, int(st_min * 1000)]  # Giả sử STmin tính bằng miligiây

    # Tạo thông điệp CAN với arbitration_id và dữ liệu fc_frame_data
    msg = can.Message(arbitration_id=0x123, data=fc_frame_data, is_extended_id=False)

    try:
        bus.send(msg)
        
    except can.CanError as e:
        print(f"Error sending Flow Control: {e}")
