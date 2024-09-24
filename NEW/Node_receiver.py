import can
import ics
import time
from Can_TP import receive_can_tp_messages
from enum import Enum

# Global list to store data from received CAN TP frames
received_data_list = []

def setup_virtual_can_bus():
    # Use a virtual CAN interface for simulation
    return can.Bus(interface='virtual', channel = 1, bitrate = 1000000, receive_own_messages = True)

def process_received_data(bus):
    global received_data_list  # Khai báo biến toàn cục

    # Nhận các thông điệp CAN TP bằng mô-đun Can_TP
    full_message = receive_can_tp_messages(bus)

    if full_message:
        print(full_message.decode('utf-8'))
    else:
        print("Không có khung nào được nhận.")

