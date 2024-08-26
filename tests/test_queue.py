import pika

from sms_circus.queue import declare_queue


class TestQueue:
    # Successfully declares a dead-letter exchange and queue
    def test_successful_dead_letter_declaration(self, mocker):
        mock_channel = mocker.MagicMock()
        mock_connection = mocker.MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock_blocking_connection = mocker.patch(
            "pika.BlockingConnection", return_value=mock_connection
        )

        queue_name = "test_queue"
        host = "test_localhost"

        channel = declare_queue(queue_name, host)
        assert mock_channel == channel

        dl_queue_name = f"{queue_name}_dead_letter"
        dl_exchange_name = f"{dl_queue_name}_exchange"
        dl_exchange_routing_key = f"{dl_exchange_name}_routing_key"

        mock_blocking_connection.assert_called_once_with(
            pika.ConnectionParameters(host=host)
        )
        mock_channel.exchange_declare.assert_called_once_with(
            exchange=dl_exchange_name, exchange_type="direct"
        )
        mock_channel.queue_declare.assert_any_call(queue=dl_queue_name, durable=True)
        mock_channel.queue_bind.assert_called_once_with(
            exchange=dl_exchange_name,
            queue=dl_queue_name,
            routing_key=dl_exchange_routing_key,
        )
        args = {
            "x-dead-letter-exchange": dl_exchange_name,
            "x-dead-letter-routing-key": dl_exchange_routing_key,
        }
        mock_channel.queue_declare.assert_any_call(
            queue=queue_name, durable=True, arguments=args
        )
        mock_channel.basic_qos.assert_called_once_with(prefetch_count=1)
