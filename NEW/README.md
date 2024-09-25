Mô Phỏng CAN TP với python-can
Dự án này mô phỏng giao thức CAN Transport Protocol (CAN TP) sử dụng thư viện python-can. Mô phỏng này bao gồm hai node:

Node Gửi: Gửi các thông điệp CAN theo từng phân đoạn.
Node Nhận: Nhận các thông điệp này, quản lý flow control và ghép các thông điệp lại thành một chuỗi hoàn chỉnh.
Các Tính Năng Đã Được Triển Khai
Xử lý Giao thức CAN TP:

Quản lý độ dài dữ liệu trong các khung CAN một cách chính xác.
Xử lý flow control bằng cách gửi các khung flow control từ node nhận để tránh bị timeout.
Xử lý padding bằng cách loại bỏ các bit đệm dư thừa trong dữ liệu nhận được.
Ghép Nối Thông Điệp:

Ghép nối các thông điệp CAN được phân đoạn từ các byte array thành một chuỗi hoàn chỉnh.
Sử dụng các khung Flow Control (FC) để đảm bảo nhận đúng các khung liên tiếp.
Cấu Trúc Dự Án
Node Gửi: Liên tục gửi các thông điệp theo định dạng CAN TP.
Node Nhận: Lắng nghe các thông điệp đến, xử lý chúng và gửi các khung flow control phù hợp.
Cả hai node hoạt động trong một vòng lặp:

Node Gửi bắt đầu gửi dữ liệu.
Node Nhận đợi dữ liệu và gửi các phản hồi flow control để quản lý thời gian và tránh timeout.
Các Thư Viện Cần Thiết
python-can:

Dùng để xử lý giao tiếp CAN.
Cài đặt bằng pip:
bash
Sao chép mã
pip install python-can
ics (nếu cần):

Thư viện tùy chọn cho các thiết lập phần cứng CAN cụ thể (NeoVi).
Cài đặt bằng pip:
bash
Sao chép mã
pip install ics
Module Can_TP:

Xử lý các chức năng giao thức CAN TP như phân đoạn thông điệp và ghép nối chúng lại.
Cách Hoạt Động
Node Gửi
Node gửi chia nhỏ một thông điệp CAN thành các khung nhỏ hơn (tùy theo đặc điểm của CAN 2.0 hoặc CAN FD). Nó gửi một hoặc nhiều khung, chờ phản hồi flow control từ node nhận, và tiếp tục gửi.

Node Nhận
Node nhận:

Nhận các khung và đảm bảo xử lý chúng theo giao thức CAN TP.
Gửi các phản hồi flow control (ví dụ: FC_CONTINUOUS) để đảm bảo node gửi không bị timeout.
Loại bỏ các bit padding từ các thông điệp nhận được và ghép dữ liệu thành một chuỗi hoàn chỉnh.
Ví Dụ Sử Dụng
python
Sao chép mã
# Node Gửi (mã giả)
def transmit_data(bus, data):
    frames = can_tp_send(data, is_can_fd=False)
    for frame in frames:
        bus.send(frame)
        # Chờ phản hồi flow control

# Node Nhận (mã giả)
def receive_data(bus):
    while True:
        frame = bus.recv()
        process_received_frame(frame)
        send_flow_control_if_needed()
Cải Tiến Tương Lai
Mở rộng chức năng để xử lý mạng CAN TP nhiều node.
Triển khai xử lý lỗi mạnh mẽ hơn cho các trường hợp mất khung hoặc nhận sai khung.