import can
import ics
import time
def send_one():
    try:
        # ics.GetDLLVersion()
        with can.Bus(interface='neovi', channel=1, bitrate=1000000) as bus:
            while 1:
                msg = can.Message(arbitration_id=0x123, data=[0x11, 0x22, 0x33, 0x44], is_extended_id=False)
                bus.send(msg)
                print("Message sent successfully")
                # time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")
        # ics.find_devices()
       
send_one()