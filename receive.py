import can
import ics
import time
def receive_one():
    try:
        # Create a CAN bus connection
        with can.Bus(interface='neovi', channel=1, bitrate=1000000) as bus:
            print("Waiting to receive messages...")
            while True:
                # Receive a message from the CAN bus
                msg = bus.recv(timeout=1)  # Wait for 1 second for a message
                if msg:
                    print(f"Received message: ID = {hex(msg.arbitration_id)}, Data={msg}")
                else:
                    print("No message received within the timeout period.")
                time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")
        # ics.find_devices().

receive_one()
