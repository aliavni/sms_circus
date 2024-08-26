import pika
from pika.adapters.blocking_connection import BlockingChannel


def declare_queue(queue_name: str, host: str) -> BlockingChannel:
    params = pika.ConnectionParameters(host=host)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # dead-letter queue
    dl_queue_name = f"{queue_name}_dead_letter"
    dl_exchange_name = f"{dl_queue_name}_exchange"
    dl_exchange_routing_key = f"{dl_exchange_name}_routing_key"

    channel.exchange_declare(exchange=dl_exchange_name, exchange_type="direct")
    channel.queue_declare(queue=dl_queue_name, durable=True)
    channel.queue_bind(
        exchange=dl_exchange_name,
        queue=dl_queue_name,
        routing_key=dl_exchange_routing_key,
    )

    # main queue
    args = {
        "x-dead-letter-exchange": dl_exchange_name,
        "x-dead-letter-routing-key": dl_exchange_routing_key,
    }
    channel.queue_declare(queue=queue_name, durable=True, arguments=args)
    channel.basic_qos(prefetch_count=1)

    return channel
