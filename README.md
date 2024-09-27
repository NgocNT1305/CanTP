Giới thiệu
Dự án này hướng dẫn cách sử dụng thư viện python-can để giả lập một node nhận và xử lý các message theo giao thức CAN Transport Protocol (CanTP). CanTP được sử dụng để truyền tải dữ liệu lớn hơn giới hạn 8 byte của giao thức CAN. Node nhận sẽ lắng nghe và xử lý dữ liệu phân đoạn từ node truyền, đồng thời gửi Flow Control (FC) để quản lý việc truyền liên tục các khung dữ liệu.

Yêu cầu chính
Nhận dữ liệu chính xác: Node nhận sẽ phải xử lý và nhận đúng độ dài dữ liệu của message.
Quản lý Flow Control: Gửi các frame Flow Control về node truyền để tránh bị flow control timeout.
Xóa bit padding: Loại bỏ các bit padding thừa (nếu có) trong quá trình nhận dữ liệu.
Ghép dữ liệu: Ghép các khung bytearray nhận được thành một chuỗi hoàn chỉnh và in ra kết quả.
Cấu trúc dự án
Sao chép mã

CanTP_Receiver_Project/
│
├── can_tp_receiver.py        # Node nhận CanTP message
├── utils.py                  # Các hàm hỗ trợ (xử lý padding, hợp nhất dữ liệu)
├── README.md                 # Tài liệu hướng dẫn
└── requirements.txt          # Danh sách thư viện cần thiết

Hướng dẫn cài đặt
Yêu cầu
Cài đặt Python 3.x.
Cài đặt thư viện cần thiết bằng lệnh:
bash
Sao chép mã
pip install -r requirements.txt
Hướng dẫn chạy Node nhận
Node nhận sẽ lắng nghe các frame CanTP và xử lý chúng. Để chạy node nhận, bạn có thể sử dụng lệnh sau:

bash
Sao chép mã
python can_tp_receiver.py
Ví dụ sử dụng
Node nhận sẽ thực hiện các bước sau:

Chờ nhận message từ node truyền: Tạo một vòng lặp để chờ dữ liệu từ node truyền.
Xử lý dữ liệu CanTP: Nhận từng phần dữ liệu, ghép lại với nhau, và gửi frame Flow Control để đảm bảo việc truyền diễn ra liên tục.
Ghép dữ liệu: Sau khi nhận đủ dữ liệu, node sẽ ghép bytearray thành một chuỗi hoàn chỉnh và in kết quả.
Ví dụ mã lệnh trong can_tp_receiver.py:

python
Sao chép mã
from can_tp_receiver import NodeReceiver

# Khởi tạo node nhận với kênh CAN phù hợp
node = NodeReceiver(channel='vcan0')

# Bắt đầu quá trình nhận dữ liệu CanTP
node.receive_data()
Giải thích chi tiết
Flow Control (FC): Node nhận sẽ gửi các frame Flow Control để điều khiển tốc độ truyền các khung Consecutive Frame (CF) từ node truyền, đảm bảo tránh bị quá tải dữ liệu.
Xóa bit padding: Sau khi nhận dữ liệu, node sẽ kiểm tra và loại bỏ các bit padding không cần thiết để đảm bảo dữ liệu được ghép lại chính xác.
Ghép bytearray thành chuỗi: Sau khi nhận đủ tất cả các khung, node sẽ hợp nhất bytearray thành một chuỗi hoàn chỉnh và in ra.
Kiến trúc CanTP Frame
Single Frame (SF): Chứa toàn bộ message nếu message nhỏ hơn 8 byte.
First Frame (FF): Được sử dụng nếu message lớn hơn 8 byte, chứa một phần dữ liệu và thông tin về độ dài tổng cộng của message.
Consecutive Frame (CF): Các khung liên tiếp được gửi sau First Frame chứa phần còn lại của dữ liệu.
Flow Control (FC): Được gửi bởi node nhận để điều khiển tốc độ truyền của các khung liên tiếp.
Tùy chỉnh
Thay đổi kênh CAN: Kênh CAN mặc định là vcan0. Bạn có thể thay đổi kênh phù hợp với phần cứng của mình bằng cách chỉnh tham số channel trong mã nguồn.
Gỡ lỗi và xử lý sự cố
Flow Control Timeout: Nếu node truyền không nhận được frame Flow Control trong thời gian quy định, có thể dẫn đến timeout. Đảm bảo rằng node nhận và node truyền đang hoạt động đúng cách và không bị mất kết nối.
