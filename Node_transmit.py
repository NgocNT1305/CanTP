# Node_transmit.py

import can
import time
import ics

from Can_TP import can_tp_send

"""==================================================================
Script: 
=====================================================================
"""
DATA = "The CanTp module shall not accept the receiving or the transmission of N-SDU with the same identifier in parallel, because otherwise the received frames cannot be assigned to the correct connection."

# # Đặt giá trị tối đa cho số phần tử
# max_elements = 256  # Thay đổi giá trị này theo nhu cầu của bạn

# # Vòng lặp để điền số phần tử vào DATA
# for i in range(max_elements):
#     DATA.append(i)

def setup_virtual_can_bus():
    return can.Bus(interface='virtual', channel = 1, bitrate = 1000000, receive_own_messages = True)

def send_data(bus):
    frames = can_tp_send(DATA, is_can_fd=False)
    for frame in frames:
        msg = can.Message(
            arbitration_id=0x123,
            data=frame,
            is_extended_id=False
        )
        try:
            bus.send(msg)
            time.sleep(0.1)
        except Exception as e:
            print(f"An error occurred: {e}")


