import can
import time
from Can_TP import receive_can_tp_messages

def setup_virtual_can_bus():
    return can.Bus(interface='virtual', channel=1, bitrate=1000000, receive_own_messages=True)

def setup_neovi_bus():
    return can.Bus(interface='neovi', channel=1, bitrate=1000000)

def process_received_data(bus):
    """Process incoming CAN messages."""
    full_message = receive_can_tp_messages(bus)

    if full_message:
        print(f"Received message: {full_message.decode('utf-8')}")
    else:
        print("No frames received.")

if __name__ == "__main__":
    use_virtual_bus = False  # Set to True to use the virtual bus

    if use_virtual_bus:
        bus = setup_virtual_can_bus()
    else:
        bus = setup_neovi_bus()

    try:
        while True:
            print("Receive data from the bus")
            process_received_data(bus)
            time.sleep(0.1)  # Delay to prevent high CPU usage
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        bus.shutdown()
