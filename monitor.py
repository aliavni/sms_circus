from time import sleep

import pandas as pd
import psycopg2
import psycopg2.extras
import streamlit as st

from sms_circus.common.db import get_connection


def get_data() -> pd.DataFrame:
    conn = get_connection()
    conn.set_session(readonly=True)
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

col_sent, col_failed = st.columns(2)

sent = records[~records["failed"]]
metric_sent_messages_label = "Sent messages"
if len(sent):
    sent_count = len(sent)
    metric_sent_messages = col_sent.metric(metric_sent_messages_label, sent_count)

failed = records[records["failed"]]
metric_failed_count_label = "Failed messages"
if len(failed):
    failed_count = len(failed)
    metric_failed_count = col_failed.metric(metric_failed_count_label, failed_count)


col_avg_sent, col_avg_failed = st.columns(2)

avg_sent_label = "Average time per sent "
if len(sent):
    avg_sent = col_avg_sent.metric(
        avg_sent_label, sent["time_to_message_seconds"].mean().round(2)
    )

avg_failed_label = "Average time per failed "
if len(failed):
    avg_failed = col_avg_failed.metric(
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
