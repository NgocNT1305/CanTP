#=============================================================================================================
# Can_TP.py
#=============================================================================================================
import can
import time
import ics
from enum import Enum
 
#Can type includes Can 2.0 and Can FD
class CAN_TYPE(Enum):
    CAN_2_0_MAX_PAYLOAD = 8  # 8 bytes for CAN 2.0
    CAN_FD_MAX_PAYLOAD = 64  # 64 bytes for CAN FD
 
NAbyte = 0x00
 
# PCI types
class PCI_types(Enum):
    PCI_SF = 0x00  # Single Frame
    PCI_FF = 0x10  # First Frame
    PCI_CF = 0x20  # Consecutive Frame
    PCI_FC = 0x30  # Flow Control
 
class FS_types(Enum):
    FC_CONTINOUS    = 0x00
    FC_WAIT         = 0x01
    FC_OVERFLOW     = 0x02
 
class PADDING(Enum):
    BYTE_PADDING    = 0x00
 
#=============================================================================================================
#=============================================================================================================
 
 
def send_single_frame(bus, data, is_can_fd = False):
    max_payload = CAN_TYPE.CAN_FD_MAX_PAYLOAD.value if is_can_fd else CAN_TYPE.CAN_2_0_MAX_PAYLOAD.value
    data_length = len(data)
    pci_byte = PCI_types.PCI_SF.value | data_length
    frame_data = [pci_byte] + list(data)
 
    while len(frame_data) < max_payload:
        frame_data.append(PADDING.BYTE_PADDING.value)
 
    message = can.Message (arbitration_id = 0x123, data = frame_data, is_extended_id = False)
    bus.send(message)
    print(f"Send single frame: {message}")  
 
#=============================================================================================================
#=============================================================================================================
 
def send_multi_frame(bus, data, is_can_fd = False):
    data_length = len(data)
    pci_byte_1 = PCI_types.PCI_FF.value | (data_length >> 8)
    pci_byte_2 = data_length & 0xFF
 
    first_frame_data = [pci_byte_1, pci_byte_2] + list(data[0:6])
    message = can.Message (arbitration_id = 0x123, data = first_frame_data, is_extended_id = False)
    bus.send(message)
    print(f"Send First frame: {message}")
 
    frame_index = 1
    remaining_data = data[6:]
 
    while remaining_data:
        flow_status, block_size, st_min = wait_flow_control(bus)
        if flow_status == FS_types.FC_CONTINOUS.value:
            while remaining_data:
                pci_byte = PCI_types.PCI_CF.value | (frame_index & 0x0F)
                consecutive_frame = [pci_byte] + list(remaining_data[:7])
 
                while len(consecutive_frame) < 8:
                    consecutive_frame.append(PADDING.BYTE_PADDING.value)
 
                    message = can.Message (
                        arbitration_id = 0x123,
                        data = consecutive_frame,
                        is_extended_id = False,
                        is_fd = False)
                   
                bus.send(message)
                print(f"Send consecutive frame: {frame_index}: {message}")
                remaining_data = remaining_data[7:]
                frame_index += 1
 
                if frame_index == block_size:
                    frame_index = 1
                    flow_status, block_size, st_min = wait_flow_control(bus)
 
 
 
#=============================================================================================================
#=============================================================================================================
 
 
def send_flow_control(bus, flow_status = FS_types.FC_CONTINOUS.value, block_size = 15, ST_min = 0):
    pci_byte = PCI_types.PCI_FC.value | flow_status
    flow_control_frame = [pci_byte, block_size, ST_min, NAbyte, NAbyte, NAbyte]
    message = can.Message (arbitration_id = 0x123, data = flow_control_frame, is_extended_id = False)
    bus.send(message)
    print(f"Send Flow control frame: {message}")
 
 
 
#=============================================================================================================
#=============================================================================================================
 
def wait_flow_control(bus):
    while True:
        msg : can.Message = bus.recv(timeout = 2)
        if msg:
            print("Dataaaaaaaaa")
            data = msg.data
            if msg.data[0] == PCI_types.PCI_FC.value:
                flow_status = data[0] & 0x0F
                block_size = data[1]
                st_min = data[2]
                return flow_status, block_size, st_min
 
#=============================================================================================================
#=============================================================================================================
 
 
def receive_can_tp_messages(bus):
    received_frames = []
    block_size = 15
    current_sn = 1
    data_length = 0
    remaining_length = 0
 
    while True:
        msg : can.Message = bus.recv(timeout = 1)
 
        if msg:
            if msg.arbitration_id != 0:
               
                pci_byte = msg.data[0] & 0xF0
 
                if pci_byte == PCI_types.PCI_SF.value:
                    SF_datalength = msg.data[0] & 0x0F
                    data = msg.data[1:1 + SF_datalength]
                    print(f"Single Frame received: {list(data)}, Data length: {SF_datalength}")
                    received_frames.append(list(data))
                    break
 
                #First Frame (FF)
                elif pci_byte == PCI_types.PCI_FF.value:
                    if msg.data[0] != 0:
                        data_length = ((msg.data[0] & 0x0F) << 8) + msg.data[1]
                        print(f"Data length = {data_length}")
                        data = msg.data[2:]
                    else:
                        data_length = (msg.data[2] << 24) | (msg.data[3] << 16) | (msg.data[4] << 8) | msg.data[5]
                        data = msg.data[6:]
                    remaining_length = data_length - len(data)
                    print(f"Data length = {data_length}")
                    print(f"remaining_length = {remaining_length}")
                    print(f"First Frame received: {list(data)}, Data length: {data_length}")
                    received_frames.append(list(data))
                    send_flow_control(bus, FS_types.FC_CONTINOUS.value, block_size = block_size, ST_min = 0)
 
                #Consecutive Frame (CF)
                elif pci_byte == PCI_types.PCI_CF.value:
                    sn = msg.data[0] & 0x0F
                    if sn == current_sn:
                        data = msg.data[1:remaining_length+1]
                        received_frames.append(list(data))
                        remaining_length -= len(data)
                        current_sn += 1
                        print(f"Consecutive Frame received: {list(data)}, Remaining length: {remaining_length}")
 
                        if current_sn == block_size:
                            send_flow_control(bus, FS_types.FC_CONTINUE.value, block_size = block_size, st_min = 0)
 
                # if pci_byte == PCI_types.PCI_FC.value:
                #     flow_status = msg.data[0] & 0x0F
                #     block_size = msg.data[1]
                #     st_min = msg.data[2]
                #     print(f"Flow Control Frame received: FS={flow_status}, Block Size={block_size}, STmin={st_min}")
        if remaining_length < 0:
            print(f"All frames received. Total data length: {data_length}")
            break
        full_message = bytearray()
        for frame in received_frames:
            if isinstance(frame, list):
                full_message.extend(bytearray(frame))
    return received_frames