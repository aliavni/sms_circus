import json
from datetime import datetime

import emoji
import psycopg2
import pytest
from pika.spec import Basic

from sms_circus.constants import QUEUE_NAME
from sms_circus.sender import Sender, SimulatedFailure


class TestSender:
    start = datetime.now()
    end = datetime.now()
    body_json = {"phone": "1234567890", "message": "Test message"}

    def test_sender_initialization(self):
        name = "TestSender"
        mean_processing_time = 5
        failure_rate = 0.2

        sender = Sender(name, mean_processing_time, failure_rate)

        assert sender.name == name
        assert sender.mean_processing_time == mean_processing_time
        assert sender.failure_rate == failure_rate

    def test_simulated_failure_handling(self, mocker):
        mock_channel = mocker.MagicMock()
        mock_method = mocker.MagicMock()
        mock_properties = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()

        mocker.patch("sms_circus.sender.random.random", return_value=0.5)
        mock_print = mocker.patch("sms_circus.sender.print")

        with pytest.raises(SimulatedFailure):
            sender = Sender("TestSender", 5, 1.0)
            sender.process_sms_and_simulate_error(
                mock_channel,
                mock_method,
                mock_properties,
                self.start,
                self.end,
                self.body_json["phone"],
                self.body_json["message"],
                mock_cursor,
            )

        # Ensure print, execute and basic_ack was not called due to the failure
        mock_print.assert_not_called()
        mock_cursor.execute.assert_not_called()
        mock_channel.basic_ack.assert_not_called()

    def test_process(self, mocker):
        mock_channel = mocker.MagicMock()
        mock_method = mocker.MagicMock()
        mock_properties = mocker.MagicMock()
        mock_cursor = mocker.MagicMock()

        mocker.patch("sms_circus.sender.random.random", return_value=0.5)
        mock_print = mocker.patch("sms_circus.sender.print")

        sender = Sender("TestSender", 5, 0)
        sender.process_sms_and_simulate_error(
            mock_channel,
            mock_method,
            mock_properties,
            self.start,
            self.end,
            self.body_json["phone"],
            self.body_json["message"],
            mock_cursor,
        )

        mock_print.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_channel.basic_ack.assert_called_once_with(
            delivery_tag=mock_method.delivery_tag
        )

    def test_sms_processed_successfully(self, mocker):
        mocker.patch("psycopg2.connect")
        mock_cursor = mocker.MagicMock()
        psycopg2.connect.return_value.cursor.return_value = mock_cursor

        mock_channel = mocker.MagicMock()
        mock_method = mocker.MagicMock(delivery_tag=Basic.Deliver)
        mock_properties = mocker.MagicMock()
        body = json.dumps(self.body_json).encode()

        sender = Sender(name="TestSender", mean_processing_time=1, failure_rate=0.0)

        sender.send_callback(mock_channel, mock_method, mock_properties, body)

        mock_cursor.execute.assert_called()
        mock_channel.basic_ack.assert_called_with(delivery_tag=mock_method.delivery_tag)

    def test_random_failure_occurs(self, mocker):
        mocker.patch("psycopg2.connect")
        mock_cursor = mocker.MagicMock()
        psycopg2.connect.return_value.cursor.return_value = mock_cursor

        mock_channel = mocker.MagicMock()
        mock_method = mocker.MagicMock(delivery_tag=Basic.Deliver)
        mock_properties = mocker.MagicMock()
        body = json.dumps(self.body_json).encode()

        sender = Sender(
            name="TestSender", mean_processing_time=1, failure_rate=1.0
        )  # 100% failure rate
        sender.send_callback(mock_channel, mock_method, mock_properties, body)

        mock_cursor.execute.assert_called()
        mock_channel.basic_reject.assert_called_with(
            delivery_tag=mock_method.delivery_tag, requeue=False
        )

    # Sender starts and prints start message with emoji
    def test_sender_starts_and_prints_start_message_with_emoji(self, mocker):
        mock_channel = mocker.patch("sms_circus.sender.declare_queue")
        mock_basic_consume = mock_channel.return_value.basic_consume = (
            mocker.MagicMock()
        )
        mock_start_consuming = mock_channel.return_value.start_consuming = (
            mocker.MagicMock()
        )
        mock_print = mocker.patch("sms_circus.sender.print")

        sender = Sender(name="TestSender", mean_processing_time=1)
        sender.start_sending()

        mock_print.assert_called_once_with(
            emoji.emojize("TestSender started :chequered_flag:")
        )
        mock_basic_consume.assert_called_once_with(
            queue=QUEUE_NAME, on_message_callback=sender.send_callback
        )
        mock_start_consuming.assert_called_once_with()
