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
 
 
class MAXFRAMETYPE(Enum):
    CAN_20_MAX_DATA = 8                          
    CAN_FD_MAX_DATA = 64                              
 
    MAX_PAYLOAD_CONSECUTIVE_CAN_20_FRAME = 7                  
    MAX_PAYLOAD_SINGLE_CAN_20_FRAME = 7                        
    MAX_PAYLOAD_FIRST_CAN_20_FRAME_DATA_LESS_THAN_4095 = 6  
    MAX_PAYLOAD_FIRST_CAN_20_FRAME_DATA_BIG_THAN_4095 = 2  
 
    MAX_PAYLOAD_CONSECUTIVE_FD_FRAME = 63                      
    MAX_PAYLOAD_SINGLE_FD_FRAME = 63                            
    MAX_PAYLOAD_FIRST_FD_FRAME_DATA_LESS_THAN_4095 = 62      
    MAX_PAYLOAD_FIRST_FD_FRAME_DATA_BIG_THAN_4095 = 58      
 
#=============================================================================================================
#=============================================================================================================

def send_one_frame(bus, data, is_can_fd=False):
    message = can.Message(arbitration_id=0x123, data=data, is_extended_id=False)
    bus.send(message)

 
def send_single_frame(bus, data, is_can_fd = False):
    max_payload = CAN_TYPE.CAN_FD_MAX_PAYLOAD.value if is_can_fd else CAN_TYPE.CAN_2_0_MAX_PAYLOAD.value
    data_length = len(data)
    pci_byte = PCI_types.PCI_SF.value | data_length
    frame_data = [pci_byte] + list(data)
 
    while len(frame_data) < max_payload:
        frame_data.append(PADDING.BYTE_PADDING.value)
    message = can.Message (arbitration_id = 0x123, data = frame_data, is_extended_id = False)
    bus.send(message)
    print(f"Send frame: {message}")  
 
#=============================================================================================================
#=============================================================================================================
 
def send_multi_frame(bus, data, is_can_fd = False):
    data_length = len(data)
    pci_byte_1 = PCI_types.PCI_FF.value | (data_length >> 8)
    pci_byte_2 = data_length & 0xFF
 
    first_frame_data = [pci_byte_1, pci_byte_2] + list(data[0:6])
    send_one_frame(bus, data = first_frame_data, is_can_fd = False)
    sequence_number = 0
    remaining_data = data[6:]
    print(f"Send First frame: {first_frame_data}")
 
    while remaining_data:
        flow_status, block_size, st_min = wait_flow_control(bus)
        if flow_status == FS_types.FC_CONTINOUS.value:
            max_payload = MAXFRAMETYPE.MAX_PAYLOAD_CONSECUTIVE_FD_FRAME.value if is_can_fd else MAXFRAMETYPE.MAX_PAYLOAD_CONSECUTIVE_CAN_20_FRAME.value
            while remaining_data:
                SDU_size = min(max_payload, len(remaining_data))
                pci_byte = PCI_types.PCI_CF.value | (sequence_number & 0x0F)
                consecutive_frame = [pci_byte] + list(remaining_data[:SDU_size])
   
                while len(consecutive_frame) < 8:
                    consecutive_frame.append(PADDING.BYTE_PADDING.value)
                
                send_one_frame(bus, data = consecutive_frame, is_can_fd = False)
                sequence_number += 1
                print(f"Send Consecutive frame {sequence_number}: {consecutive_frame}")

                remaining_data = remaining_data[SDU_size:]
                # print(f"Remaining data: {remaining_data}")
 
                if (sequence_number % block_size == 0):
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
            print(f"Flow control received: {msg.data}")
            data = msg.data
            if msg.data[0] == PCI_types.PCI_FC.value:
                flow_status = data[0] & 0x0F
                block_size = data[1]
                st_min = data[2]
                return flow_status, block_size, st_min
 
#=============================================================================================================
#=============================================================================================================
 
 
def receive_can_tp_messages(bus):
    Full_received_frames = []
    frame_receiverd = 0
    block_size = 15
    current_sn = 0
    data_length = 0
 
    while True:
        msg : can.Message = bus.recv(timeout = 1)
 
        if msg:
            if msg.arbitration_id != 0:
               
                pci_byte = msg.data[0] & 0xF0
 
                if pci_byte == PCI_types.PCI_SF.value:
                    SF_datalength = msg.data[0] & 0x0F
                    data = msg.data[1:1 + SF_datalength]
                    print(f"Single Frame received: {list(data)}, Data length: {SF_datalength}")
                    Full_received_frames.append(list(data))
                    break
 
                #First Frame (FF)
                elif pci_byte == PCI_types.PCI_FF.value:
                    if msg.data[1] == 0:
                        data_length == msg.data[2:]
                    else:
                        data_length = msg.data[0] << 4 + msg.data[1]
                       
                    if data_length >= 100000:
                        send_flow_control(bus, FS_types.FC_OVERFLOW.value, block_size = block_size, ST_min = 0)
                        break
                    frame_receiverd = 0
                    print(f"First Frame received: {list(Full_received_frames)}, Data length: {data_length}")
                    send_flow_control(bus, FS_types.FC_CONTINOUS.value, block_size = block_size, ST_min = 0)
 
                #Consecutive Frame (CF)
                elif pci_byte == PCI_types.PCI_CF.value:
                    current_sn = msg.data[0] & 0x0F
                    Full_received_frames += msg.data[1:]
                    print(f"Consecutive Frame received: {list(data)}")
                    frame_receiverd += 1
                    if current_sn == block_size:
                        send_flow_control(bus, FS_types.FC_CONTINOUS.value, block_size = block_size, ST_min = 0)
               
        if Full_received_frames ==  data_length:
            print(f"All frames received.")
            break
    return Full_received_frames