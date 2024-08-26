import pytest

from sms_circus.constants import (
    DEFAULT_NUMBER_OF_MESSAGES,
    QUEUE_NAME,
    RABBIT_HOST,
)
from sms_circus.producer import Producer


class TestProducer:
    @pytest.mark.parametrize(
        "num_messages", [0, 100, DEFAULT_NUMBER_OF_MESSAGES, 10000]
    )
    def test_produce_default_number_of_messages(self, num_messages, mocker):
        mock_channel = mocker.patch("sms_circus.producer.declare_queue")
        mock_channel.return_value = mocker.MagicMock()
        mock_basic_publish = mock_channel.return_value.basic_publish

        producer = Producer(num_messages)
        producer.produce_messages()

        mock_channel.assert_called_once_with(host=RABBIT_HOST, queue_name=QUEUE_NAME)
        assert mock_basic_publish.call_count == num_messages

        if num_messages > 0:
            call_kwargs = mock_basic_publish.call_args.kwargs
            assert set(call_kwargs) == {"routing_key", "properties", "exchange", "body"}
            assert call_kwargs["exchange"] == ""
            assert call_kwargs["routing_key"] == QUEUE_NAME
