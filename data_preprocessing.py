import re
from configparser import ConfigParser
import pandas as pd
from pathlib import Path
import os
# from tqdm.auto import tqdm
import typer
import numpy as np


def clean_df(raw_messages_df: pd.DataFrame, members_df: pd.DataFrame) -> pd.DataFrame:

    # replace na rows with empty strings
    raw_messages_df["content"] = raw_messages_df["content"].apply(
        lambda x:
        x if pd.notnull(x) else " "
    )

    # replace urls
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    def replace_url(text):
        span = re.search(url_regex, text).span()
        return text[:span[0]] + "url" + text[span[1]:]

    def replace_all_url_tokens(text):
        while re.search(url_regex, text) is not None:
            text = replace_url(text)
        return text

    raw_messages_df["content"] = raw_messages_df["content"].apply(
        replace_all_url_tokens)

    # replace discord emojis with their names
    emoji_regex = r'<:.*?:[0-9]+>'

    def replace_emoji(text):
        span = re.search(emoji_regex, text).span()
        emojiName = text[span[0]:span[1]].split(':')[1]
        return text[:span[0]] + emojiName + text[span[1]:]

    def replace_all_emoji_tokens(text):
        while re.search(emoji_regex, text) is not None:
            text = replace_emoji(text)
        return text

    raw_messages_df["content"] = raw_messages_df["content"].apply(
        replace_all_emoji_tokens)
    raw_messages_df.head(3)

    # replace user mentions with their names
    user_regex = r'<@[0-9]+>'

    def replace_user_token(text):
        span = re.search(user_regex, text).span()
        user_id = text[span[0]+2:span[1]-1]
        try:
            user_name = members_df[members_df["id"]
                                   == int(user_id)]["name"].iloc[0]
        except IndexError:
            user_name = "Human"
        return text[:span[0]] + user_name + text[span[1]:]

    def replace_all_user_tokens(text):
        while re.search(user_regex, text) is not None:
            text = replace_user_token(text)
        return text

    raw_messages_df["content"] = raw_messages_df["content"].apply(
        replace_all_user_tokens)

    # get rid of all emoji characters
    raw_messages_df["content"] = raw_messages_df["content"].apply(
        lambda x: re.sub(r'[^\x00-\x7F]+', ' ', x))

    # replace line breaks with spaces
    raw_messages_df["content"] = raw_messages_df["content"].apply(
        lambda x: x.replace("\n", " "))

    # convert timestamp to uniform datetime
    raw_messages_df["timestamp"] = pd.to_datetime(
        raw_messages_df["timestamp"])

    # uniformly order by timestamp
    ordered_df = pd.DataFrame(columns=raw_messages_df.columns)
    for channel in raw_messages_df["channel"].unique():
        channel_messages = raw_messages_df[raw_messages_df["channel"] == channel]
        channel_messages = channel_messages.sort_values(by="timestamp")
        # POTENTIALLY PROBLEMATIC vvv
        ordered_df = pd.concat(
            [ordered_df, channel_messages], ignore_index=True)
    raw_messages_df = ordered_df

    return raw_messages_df
