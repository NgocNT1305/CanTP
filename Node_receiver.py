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
    received_frames = receive_can_tp_messages(bus)

    if received_frames:
        full_message = bytearray()
    
        print("Nội dung khung nhận được:", received_frames)
        
        # Lặp qua các khung nhận được
        for frame in received_frames:
            # Nếu frame là danh sách, hãy xử lý từng phần tử
            if isinstance(frame, list):
                full_message.extend(frame)  # Thêm dữ liệu từ danh sách khung
                received_data_list.append(frame)
            else:
                print("Khung không phải là danh sách hoặc không có thuộc tính 'data'")

