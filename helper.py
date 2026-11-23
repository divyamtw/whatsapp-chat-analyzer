from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter

import pandas as pd


def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]
    words = []
    for message in df["message"]:
        words.extend(message.split())

    num_media_messages = df[df["message"] == "<Media omitted>\n"].shape[0]

    extractor = URLExtract()
    num_links = []

    for message in df["message"]:
        num_links.extend(extractor.find_urls(message))

    return num_messages, len(words), num_media_messages, len(num_links)


def fetch_busy_users(df):
    top_busy_user = df["user"].value_counts().head()

    busy_user_percent = (
        (df["user"].value_counts() / df.shape[0] * 100)
        .reset_index()
        .rename(columns={"user": "name", "count": "percent(%)"})
        .round({"percent(%)": 2})
    )

    return top_busy_user, busy_user_percent


def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color="white")
    df_wc = wc.generate(df["message"].str.cat(sep=" "))

    return df_wc


def most_common_words(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    f = open(r"D:\Divyam\Projects\whatsapp-chat-analysis\stop_hinglish.txt", "r")
    stop_words = f.read()

    temp = df[df["user"] != "group_notification"]
    temp = temp[temp["message"] != "<Media omitted>\n"]

    words = []

    for message in temp["message"]:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    df = pd.DataFrame(Counter(words).most_common(20)).rename(
        columns={0: "word", 1: "count"}
    )

    return df
