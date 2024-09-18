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
