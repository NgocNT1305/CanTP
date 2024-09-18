# main.py

import threading
import subprocess

# Define the functions to run each script
def run_transmit():
    subprocess.run(["python", "Node_transmit.py"])

def run_receive():
    subprocess.run(["python", "Node_receiver.py"])

if __name__ == "__main__":
    # Create threads for sending and receiving
    sender_thread = threading.Thread(target=run_transmit)
    receiver_thread = threading.Thread(target=run_receive)
    
    # Start the threads
    sender_thread.start()
    receiver_thread.start()
    
    # Wait for both threads to finish
    sender_thread.join()
    receiver_thread.join()
