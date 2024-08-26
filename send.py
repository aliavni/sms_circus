import threading

from sms_circus.config import read_sender_configs
from sms_circus.sender import Sender

if __name__ == "__main__":
    sender_configs = read_sender_configs()

    sender_threads = []
    for conf in sender_configs:
        sender = Sender(**conf)
        sender_thread = threading.Thread(target=sender.start_sending)
        sender_threads.append(sender_thread)

    for sender_thread in sender_threads:
        sender_thread.start()
