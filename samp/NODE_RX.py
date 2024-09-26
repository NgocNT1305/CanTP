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
    PCI_FF = 0x10  # First Frame
    PCI_CF = 0x20  # Consecutive Frame
    PCI_FC = 0x30  # Flow Control

class FS_types(Enum):
    FC_CONTINUE     = 0x00
    FC_WAIT         = 0x01
    FC_OVERFLOW     = 0x02


def receive_can_tp_messages(bus):
    received_frames = []
    full_message = bytearray()
    block_size = 15
    current_sn = 1
    data_length = 0
    remaining_length = 0

    while True:
        msg : can.Message = bus.recv(timeout = 1)

        if msg:
            if msg.arbitration_id != 0:
                
                pci_byte = msg.data[0]

                if  (pci_byte >> 4) == PCI_types.PCI_SF.value:
                    SF_datalength = msg.data[0] & 0x0F
                    data = msg.data[1:1 + SF_datalength]
                    received_frames.append(list(data))
                    print(f"Single Frame received: {received_frames}, Data length: {SF_datalength}")
                    break

                #First Frame (FF)
                elif pci_byte  == PCI_types.PCI_FF.value:

                    if (msg.data[0] & 0x0F) < 0x0F:
                        data_length = ((msg.data[0] & 0x0F) << 8) | msg.data[1]
                        data = msg.data[2:]
                        remaining_length = data_length - len(data)
                        received_frames.append(list(data))
                        print(f"First Frame received (<= 4095): {data}, Data length: {data_length}")

                    else:
                        data_length = ((msg.data[1] << 24) | (msg.data[2] << 16) | (msg.data[3] << 8) | msg.data[4])
                        data = msg.data[5:]
                        remaining_length = data_length - len(data)
                        received_frames.append(list(data))
                        print(f"First Frame received (> 4095): {data}, Data length: {data_length}")

                    send_flow_control(bus, FS_types.FC_CONTINUE.value, block_size = block_size, st_min = 0)

                #Consecutive Frame (CF)
                elif pci_byte == PCI_types.PCI_CF.value:
                    sn = msg.data[0] & 0x0F
                    if sn == current_sn:
                        data = msg.data[1:]
                        received_frames.append(list(data))
                        remaining_length -= len(data)
                        current_sn = (current_sn + 1) % 16
                        print(f"Consecutive Frame received: {data}, Remaining length: {remaining_length}")

                        if len(received_frames) % block_size == 0:
                            send_flow_control(bus, FS_types.FC_CONTINUE.value, block_size = block_size, st_min = 0)
                
                if remaining_length <= 0:
                    print(f"All frames received. Total data length: {data_length}")
                    break

    full_message = bytearray()
    for frame in received_frames:
        if isinstance(frame, list):
            full_message.extend(bytearray(frame))

    return full_message

#===========================================================================================================

def send_flow_control(bus, frame_status, block_size=15, st_min=0):
    pci_byte = (PCI_types.PCI_FC.value) | (frame_status & 0x0F)
    fc_frame_data = [pci_byte, block_size, int(st_min * 1000)]
    fc_frame_data.extend([0x00] * (8 - len(fc_frame_data)))
    msg = can.Message(arbitration_id=0x123, data = fc_frame_data, is_extended_id=False)

    try:
        bus.send(msg)
        print(f"Flow Control sent: {fc_frame_data}")
        print(msg)

    except can.CanError as e:
        print(f"Error sending Flow Control: {e}")   


def setup_neovi_bus():
    return can.Bus(interface='neovi', channel=1, bitrate=1000000)


if __name__ == "__main__":
    bus = setup_neovi_bus()
    try:
        while True:
            print("Receive data from the bus")
            receive_can_tp_messages(bus)
            time.sleep(0.1)  # Delay to prevent high CPU usage
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()