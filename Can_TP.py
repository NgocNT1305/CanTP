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

def can_tp_send(data, is_can_fd=False):
    if isinstance(data, str):
        data = bytearray(data, 'utf-8')
    # CAN 2.0 payload is 8 bytes, CAN FD payload is 64 bytes
    max_payload = CAN_TYPE.CAN_FD_MAX_PAYLOAD.value if is_can_fd else CAN_TYPE.CAN_2_0_MAX_PAYLOAD.value
    frames = []
    data_length = len(data)

    # Calculate how many bytes can be used for data in a single frame
    if data_length <= max_payload - 1:
        # Single Frame (SF) - PCI byte takes up the first byte
        pci_byte = (PCI_types.PCI_SF.value << 4) | (data_length & 0x0F)
        frame = [pci_byte] + list(data)
        frames.append(frame)
    else:
        # First Frame (FF) - Two bytes for PCI, rest for data
        first_frame_data_length = max_payload - 2
        pci_bytes = [(PCI_types.PCI_FF.value << 4) | ((data_length >> 8) & 0x0F), data_length & 0xFF]
        frame = pci_bytes + list(data[:first_frame_data_length])
        frames.append(frame)
        # Consecutive Frames (CF) - Sequence number starts at 1
        seq_num = 1
        for i in range(first_frame_data_length, data_length, max_payload - 1):
            pci_byte = (PCI_types.PCI_CF.value << 4) | (seq_num & 0x0F)
            frame = [pci_byte] + list(data[i:i + (max_payload - 1)])
            frames.append(frame)
            seq_num = (seq_num + 1) & 0x0F  # Sequence number wraps around at 0xF

    return frames

def receive_can_tp_messages(bus):
    received_frames = []  # Lưu trữ các phần dữ liệu nhận được
    full_message = bytearray()  # Lưu trữ toàn bộ thông điệp sau khi hoàn thành
    block_size = 15  # Số lượng frame cho một block
    current_sn = 1  # Sequence number hiện tại
    data_length = 0  # Tổng độ dài dữ liệu cần nhận
    remaining_length = 0  # Số byte còn lại phải nhận

    while True:
        # Đọc một thông điệp từ bus
        msg = bus.recv(timeout=5)  # Tăng thời gian timeout nếu cần

        if msg:
            pci_byte = msg.data[0] >> 4  # Lấy 4 bit cao để xác định loại PCI

            # Xử lý Single Frame (SF)
            if pci_byte == PCI_types.PCI_SF.value:
                SF_datalength = msg.data[0] & 0x0F  # Lấy 4 bit thấp để xác định độ dài dữ liệu
                data = msg.data[1:1 + SF_datalength]  # Lấy dữ liệu từ byte 1 trở đi
                received_frames.append(list(data))  # Chuyển đổi list thành bytearray
                print(f"Single Frame received: {received_frames}, Data length: {SF_datalength}")
                break  # Thoát vì chỉ có một frame duy nhất

            # Xử lý First Frame (FF)
            elif pci_byte == PCI_types.PCI_FF.value:
                # Trường hợp dữ liệu <= 4095 byte
                if (msg.data[0] & 0x0F) < 0x0F:
                    # Lấy tổng độ dài dữ liệu từ 12 bit đầu tiên
                    data_length = ((msg.data[0] & 0x0F) << 8) | msg.data[1]
                    data = msg.data[2:]  # Lấy dữ liệu từ byte thứ 2 trở đi
                    remaining_length = data_length - len(data)
                    received_frames.append(list(data))  # Chuyển đổi list thành bytearray
                    print(f"First Frame received (<= 4095): {data}, Data length: {data_length}")

                # Trường hợp dữ liệu > 4095 byte
                else:
                    # Lấy tổng độ dài dữ liệu từ 4 byte tiếp theo
                    data_length = ((msg.data[1] << 24) | (msg.data[2] << 16) | (msg.data[3] << 8) | msg.data[4])
                    # Lấy dữ liệu từ byte thứ 5 trở đi
                    data = msg.data[5:]
                    remaining_length = data_length - len(data)
                    received_frames.append(list(data))  # Chuyển đổi list thành bytearray
                    print(f"First Frame received (> 4095): {data}, Data length: {data_length}")

                # Gửi Flow Control sau khi nhận FF
                send_flow_control(bus, fs=FS_types.FC_CONTINOUS.value, block_size=block_size, st_min=0)

            # Xử lý Consecutive Frame (CF)
            elif pci_byte == PCI_types.PCI_CF.value:
                sn = msg.data[0] & 0x0F  # Lấy Sequence Number
                if sn == current_sn:
                    # Nếu SN đúng, lưu dữ liệu và tăng SN
                    data = msg.data[1:]  # Lấy dữ liệu từ byte thứ 2 trở đi
                    received_frames.append(list(data))  # Chuyển đổi list thành bytearray
                    remaining_length -= len(data)
                    current_sn = (current_sn + 1) % 16  # Tăng SN, quay lại 0 nếu SN >= 15
                    print(f"Consecutive Frame received: {data}, Remaining length: {remaining_length}")

                    # Kiểm tra nếu nhận đủ block size thì gửi Flow Control mới
                    if len(received_frames) % block_size == 0:
                        send_flow_control(bus, fs=FS_types.FC_CONTINOUS.value, block_size=block_size, st_min=0)

            # Kiểm tra nếu đã nhận đủ dữ liệu
            if remaining_length <= 0:
                print(f"All frames received. Total data length: {data_length}")
                break  # Kết thúc khi nhận đủ dữ liệu

    # Kết hợp các frame lại thành một thông điệp đầy đủ
    full_message = bytearray()
    for frame in received_frames:
        if isinstance(frame, list):
            full_message.extend(bytearray(frame))

    return full_message


#==========================================================================

def send_flow_control(bus, fs=FS_types.FC_CONTINOUS.value, block_size=15, st_min=0):
    """
    Gửi một khung Flow Control trong CAN TP.

    :param bus: Đối tượng CAN bus mà bạn muốn gửi tin nhắn.
    :param fs: Flow Status (FS), giá trị mặc định là FC_CONTINOUS.
    :param block_size: Số lượng consecutive frames được phép gửi trước khi gửi một Flow Control khác. Mặc định là 15.
    :param st_min: Minimum separation time giữa các frames, mặc định là 0 (tính bằng giây).
    """

    # Chuẩn bị dữ liệu cho Flow Control frame
    # FS (Flow Status) là byte đầu tiên, BS (Block Size) là byte thứ hai, STmin là byte thứ ba
    fc_frame_data = [fs, block_size, int(st_min * 1000)]  # Giả sử STmin tính bằng mili-giây và nhân với 1000

    # Đảm bảo đủ 8 bytes cho frame CAN (dù không dùng hết)
    fc_frame_data.extend([0x00] * (8 - len(fc_frame_data)))  # Điền thêm 0x00 nếu dữ liệu chưa đủ 8 bytes

    # Tạo thông điệp CAN với arbitration_id và dữ liệu fc_frame_data
    msg = can.Message(arbitration_id=0x123, data=fc_frame_data, is_extended_id=False)

    try:
        # Gửi thông điệp Flow Control lên bus
        bus.send(msg)
        print(f"Flow Control sent: {fc_frame_data}")

    except can.CanError as e:
        print(f"Error sending Flow Control: {e}")
