# Can_TP.py

CAN_2_0_MAX_PAYLOAD = 8  # 8 bytes for CAN 2.0
CAN_FD_MAX_PAYLOAD = 64  # 64 bytes for CAN FD

# PCI types
PCI_SF = 0x00  # Single Frame
PCI_FF = 0x10  # First Frame
PCI_CF = 0x20  # Consecutive Frame
PCI_FC = 0x30  # Flow Control

def can_tp_send(data, is_can_fd=False):
    max_payload = CAN_FD_MAX_PAYLOAD if is_can_fd else CAN_2_0_MAX_PAYLOAD
    frames = []
    data_length = len(data)

    if data_length <= max_payload:
        # Single Frame
        pci_byte = PCI_SF | (data_length & 0x0F)
        frames.append([pci_byte] + data)
    else:
        # First Frame
        pci_bytes = [PCI_FF | ((data_length >> 8) & 0x0F), data_length & 0xFF]
        frames.append(pci_bytes + data[:max_payload - 2])

        # Consecutive Frames
        seq_num = 1
        for i in range(max_payload - 2, data_length, max_payload - 1):
            pci_byte = PCI_CF | (seq_num & 0x0F)
            frames.append([pci_byte] + data[i:i + max_payload - 1])
            seq_num = (seq_num + 1) & 0x0F  # Sequence number wraps around at 0xF

    return frames


def receive_can_tp_messages(bus):
    received_frames = []
    full_message = bytearray()
    expected_sequence_number = 1
    
    while True:
        # Read a message from the bus
        msg = bus.recv(timeout=1)
        
        if msg is None:
            print("Timeout waiting for CAN message.")
            break

        # PCI byte is the first byte of the message data
        pci_byte = msg.data[0] >> 4  # Extract the first 4 bits

        # Handle single frame
        if pci_byte == PCI_SF:
            received_frames.append(msg)
            print(f"Single frame received: {msg.data}")
            return received_frames

        # Handle first frame
        elif pci_byte == PCI_FF:
            received_frames.append(msg)
            print(f"First frame received: {msg.data}")
            # Extract and store data
            full_message.extend(msg.data[2:])  # Skip PCI and length bytes

        # Handle consecutive frame
        elif pci_byte == PCI_CF:
            sequence_number = msg.data[0] & 0x0F  # Last 4 bits
            if sequence_number == expected_sequence_number:
                received_frames.append(msg)
                print(f"Consecutive frame {sequence_number} received: {msg.data}")
                full_message.extend(msg.data[1:])  # Skip the PCI byte
                expected_sequence_number = (expected_sequence_number + 1) % 16
            else:
                print("Unexpected sequence number.")
                break
        
        # Assuming message ends when full_message has sufficient data
        # Add custom logic to determine when the message is fully received
        if message_complete(full_message):
            break
    
    return received_frames

def message_complete(full_message):
    """
    Placeholder function to determine if the message has been fully received.
    You will need to implement this logic based on your application's needs.
    """
    # Example: return True if the message has reached a certain length
    return len(full_message) >= 64  # Example condition for CAN FD