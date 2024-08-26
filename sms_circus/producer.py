import json

import pika
from faker import Faker

from sms_circus.constants import (
    DEFAULT_NUMBER_OF_MESSAGES,
    MAX_CHARS_IN_SMS,
    QUEUE_NAME,
    RABBIT_HOST,
)
from sms_circus.queue import declare_queue


class Producer:
    def __init__(self, num_messages: int = DEFAULT_NUMBER_OF_MESSAGES):
        self.num_messages = num_messages
        self.fake = Faker()

    def produce_messages(self) -> None:
        channel = declare_queue(queue_name=QUEUE_NAME, host=RABBIT_HOST)

        for _ in range(self.num_messages):
            payload = {
                "phone": self.fake.basic_phone_number(),
                "message": self.fake.text(max_nb_chars=MAX_CHARS_IN_SMS),
            }

            channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=json.dumps(payload),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                ),
            )

        print(f"Produced {self.num_messages} messages in the {QUEUE_NAME} queue.")
