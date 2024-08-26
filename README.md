# Welcome to SMS Circus


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Setup](#setup)
- [Run](#run)
- [Monitoring](#monitoring)
- [RabbitMQ](#rabbitmq)
- [Testing](#testing)
- [Intentionally ignored](#intentionally-ignored)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Setup

1. Create a `.env` file by copy/pasting the [.env.template](.env.template) file.
2. Update the `POSTGRES_PASSWORD` value in your [.env](.env) file.
3. Run docker compose

    ```bash
    docker compose up -d --build
    ```

    This may take a minute to run since services wait for RabbitMQ and Postgres to become healthy.

## Run

1. Produce messages

    You can run the following command without the `--messages 10` argument.
    In that case, the producer by default will produce 1000 messages.

    ```bash
    docker run --network=sms_circus_sms_circus -it --rm sms_circus-controller python produce.py --messages 10
    ```

2. Run senders

    There are 3 pre-defined senders (see [sender configs](sms_circus/sender_configs)) that has different behavior.
    You can start those senders with the following command:

    ```bash
    docker run  --network=sms_circus_sms_circus -it --rm sms_circus-controller python send.py
    ```

    If you are happy with how they are behaving, you can re-run the same command in a different terminal to start 3 additional senders.

## Monitoring

Monitoring is handled with a Streamlit application. You can view it by clicking on [http://localhost:8501/](http://localhost:8501/)

## RabbitMQ

RabbitMQ UI is available at [http://localhost:15672/](http://localhost:15672/). You can log in using the default credentials (hint: guest)

SMS Circus has 2 queues:

1. `sms` is the main queue. This is the queue producer will send messages to and senders will consume.
2. `sms_dead_letter` is the dead letter queue. Messages that senders cannot process will end up in this queue.

## Testing

Automated test suite is built with pytest. You can run the test suite with the following command:

```bash
docker run  --network=sms_circus_sms_circus -it --rm sms_circus-controller pytest
```

[send.py](send.py), [produce.py](produce.py) and [monitoring.py](monitoring.py) are ignored in coverage checks 😅
See the [.coveragerc](.coveragerc) file for details.

## Intentionally ignored

I did not implement logging to keep things simpler. Instead I am using print statements for logging.
