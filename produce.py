import argparse

from sms_circus.constants import DEFAULT_NUMBER_OF_MESSAGES
from sms_circus.producer import Producer

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Produce a specified number of messages."
    )
    parser.add_argument(
        "--messages",
        type=int,
        default=DEFAULT_NUMBER_OF_MESSAGES,
        required=False,
        help="The number of messages to produce",
    )
    args = parser.parse_args()

    producer = Producer(num_messages=args.messages)
    producer.produce_messages()
