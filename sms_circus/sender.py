import json
import random
import time
from datetime import datetime

import emoji
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from sms_circus.common.db import get_connection
from sms_circus.constants import QUEUE_NAME, RABBIT_HOST
from sms_circus.queue import declare_queue


class SimulatedFailure(Exception):
    pass


class Sender:
    def __init__(self, name: str, mean_processing_time: int, failure_rate: float = 0.1):
        self.name = name
        self.mean_processing_time = mean_processing_time
        self.failure_rate = failure_rate

    def process_sms_and_simulate_error(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        start: datetime,
        end: datetime,
        phone: str,
        message: str,
        cursor,
    ) -> None:
        if random.random() < self.failure_rate:  # nosec B311
            raise SimulatedFailure(self.name)

        message = f":green_circle: {self.name} sent: {message} to phone: {phone}| Time to message: {end - start}"
        print(emoji.emojize(message))

        cursor.execute(
            "INSERT INTO messages (start_time, end_time, phone, message) VALUES (%s, %s, %s, %s)",
            [start, end, phone, message],
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_callback(
        self,
        ch: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        start = datetime.now()

        wait_time = random.uniform(0, self.mean_processing_time * 2)  # nosec B311
        time.sleep(wait_time)

        end = datetime.now()

        payload = json.loads(body)
        phone = payload["phone"]
        message = payload["message"]

        conn = get_connection()
        cursor = conn.cursor()

        try:
            self.process_sms_and_simulate_error(
                ch, method, properties, start, end, phone, message, cursor
            )
        except SimulatedFailure:
            message = f":red_circle: {self.name} failed to process: {body!r} | Time to fail: {end - start}"
            print(emoji.emojize(message))

            cursor.execute(
                "INSERT INTO messages (start_time, end_time, failed, phone, message) VALUES (%s, %s, %s, %s, %s)",
                [start, end, True, phone, message],
            )

            ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)

        conn.close()

    def start_sending(self) -> None:
        print(emoji.emojize(f"{self.name} started :chequered_flag:"))

        channel = declare_queue(QUEUE_NAME, RABBIT_HOST)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=self.send_callback)
        channel.start_consuming()
