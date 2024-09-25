import can
import time
import ics
from Can_TP import can_tp_send

def setup_virtual_can_bus():
    """Set up a virtual CAN bus interface."""
    return can.Bus(interface='virtual', channel=1, bitrate=1000000, receive_own_messages=True)

def send_data(bus, data):
    """Send data frames over the CAN bus."""
    frames = can_tp_send(data, is_can_fd=False)
    for frame in frames:
        msg = can.Message(
            arbitration_id=0x123,
            data=frame,
            is_extended_id=False
        )
        try:
            bus.send(msg)
            print(f"Sent message: {msg}")
            time.sleep(0.1)
        except Exception as e:
            print(f"An error occurred while sending CAN message: {e}")

if __name__ == "__main__":
    # Use virtual or neovi based on preference
    use_virtual_bus = False

    if use_virtual_bus:
        bus = setup_virtual_can_bus()
    else:
        bus = can.Bus(interface='neovi', channel=1, bitrate=1000000)

    try:
        user_input = input("Enter data to send (type 'exit' to quit): ")
        while True:
            if user_input.lower() == 'exit':
                print("Exiting...")
                break
            send_data(bus, user_input.encode())  # Ensure data is in bytes
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()  # Safely shutdown the CAN bus
