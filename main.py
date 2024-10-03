# # main.py
 
# import threading
# import subprocess
# import Node_receiver
# import Node_transmit
# import time
 
 
# def run_transmit():
#     subprocess.run(["python", "Node_transmit.py"])
 
# def run_receive():
#     subprocess.run(["python", "Node_receiver.py"])
 
# if __name__ == "__main__":
 
#     try:
#         bus = Node_transmit.setup_virtual_can_bus()
#         user_input = input("Enter data to send: ")
#         Node_transmit.send_frame(bus, user_input)
#         Node_receiver.process_received_data(bus)
#         time.sleep(0.1)
#     finally:
#         bus.shutdown()
    

# import can
# import threading
# import time
# from Node_receiver import receive_can_tp_messages
# from Node_transmit import send_frame


# # Tạo bus CAN ảo cho gửi và nhận
# bus_sender   = can.interface.Bus(interface='virtual', channel=1, bitrate=1000000)
# bus_receiver = can.interface.Bus(interface='virtual', channel=1, bitrate=1000000)

# # Cờ để dừng các luồng
# stop_flag = False

# # Tạo luồng cho việc gửi và nhận tin nhắn
# send_thread = threading.Thread(target=send_frame)
# receive_thread = threading.Thread(target=receive_can_tp_messages)

# # Bắt đầu các luồng
# send_thread.start()
# receive_thread.start()

# # Chờ cho các luồng kết thúc
# send_thread.join()
# receive_thread.join()

# # Tắt bus
# bus_sender.shutdown()
# bus_receiver.shutdown()

# print("End of simulation")


import can
import threading
import time
from Node_receiver import receive_can_tp_messages
from Node_transmit import send_frame

# Tạo bus CAN ảo cho gửi và nhận
bus_sender   = can.interface.Bus(interface='virtual', channel=1, bitrate=1000000)
bus_receiver = can.interface.Bus(interface='virtual', channel=1, bitrate=1000000)

# Dữ liệu mẫu để gửi
sample_data = "The material contained in this work is protected by copyright and other types of intellectual property rights. The commercial exploitation of the material contained in this work requires a license to such intellectual property rights."

# Cờ để dừng các luồng
stop_flag = False

# Tạo luồng cho việc gửi tin nhắn, truyền tham số `bus_sender` và `sample_data`
send_thread = threading.Thread(target=send_frame, args=(bus_sender, sample_data))

# Tạo luồng cho việc nhận tin nhắn
receive_thread = threading.Thread(target=receive_can_tp_messages, args=(bus_receiver,))

# Bắt đầu các luồng
send_thread.start()
receive_thread.start()

# Chờ cho các luồng kết thúc
send_thread.join()
receive_thread.join()

# Tắt bus
bus_sender.shutdown()
bus_receiver.shutdown()

print("End of simulation")
