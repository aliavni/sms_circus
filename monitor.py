import os
from time import sleep

import pandas as pd
import psycopg2
import psycopg2.extras
import streamlit as st

DB_NAME = os.getenv("POSTGRES_DB", "sms")
DB_USER = os.getenv("POSTGRES_USER", "sms")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "sms")
DB_HOST = "postgres"
DB_PORT = 5432


def get_data() -> pd.DataFrame:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT,
        host=DB_HOST,
    )
    conn.set_session(readonly=True, autocommit=True)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM messages")
    res = cursor.fetchall()

    df = pd.DataFrame(res)
    conn.close()

    df["time_to_message_seconds"] = (
        df["end_time"] - df["start_time"]
    ).dt.total_seconds()

    return df


st.title("SMS Circus Monitoring")

with st.sidebar:
    auto_refresh = st.toggle("Auto refresh", value=True)

    if auto_refresh:
        sleep_seconds = st.slider(
            "Refresh interval (seconds)",
            min_value=1,
            value=1,
        )

records = get_data()

col1, col2 = st.columns(2)

sent = records[~records["failed"]]
metric_sent_messages_label = "Sent messages"
if len(sent):
    sent_count = len(sent)
    metric_sent_messages = col1.metric(metric_sent_messages_label, sent_count)

failed = records[records["failed"]]
metric_failed_count_label = "Failed messages"
if len(failed):
    failed_count = len(failed)
    metric_failed_count = col2.metric(metric_failed_count_label, failed_count)


avg_sent_col, avg_failed_col = st.columns(2)

avg_sent_label = "Average time per sent "
if len(sent):
    avg_sent = avg_sent_col.metric(
        avg_sent_label, sent["time_to_message_seconds"].mean().round(2)
    )

avg_failed_label = "Average time per failed "
if len(failed):
    avg_failed = avg_failed_col.metric(
        avg_failed_label, failed["time_to_message_seconds"].mean().round(2)
    )

while True:
    records = get_data()

    sent = records[~records["failed"]]
    if len(sent):
        sent_count = len(sent)
        metric_sent_messages.metric(metric_sent_messages_label, value=sent_count)

    failed = records[records["failed"]]
    if len(failed):
        failed_count = len(failed)
        metric_failed_count.metric(metric_failed_count_label, value=failed_count)

    if len(sent):
        avg_sent.metric(
            avg_sent_label, value=sent["time_to_message_seconds"].mean().round(2)
        )

    if len(failed):
        avg_failed.metric(
            avg_failed_label, value=failed["time_to_message_seconds"].mean().round(2)
        )

    sleep(sleep_seconds)
