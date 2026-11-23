import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from preprocessor import preprocessor
from helper import (
    fetch_stats,
    fetch_busy_users,
    create_wordcloud,
    most_common_words,
    emoji_helper,
    monthly_timeline,
    daily_timeline,
    week_activity_map,
    month_activity_map,
    activity_heatmap,
)

st.set_page_config(page_title="Whatsapp Chat Analyzer", page_icon="㊙️", layout="wide")
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data)

    df = preprocessor(data)

    # st.title("Whatsapp Chats")
    # st.dataframe(df)

    user_list = df["user"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_links = fetch_stats(
            selected_user, df
        )
        st.title("Whatsapp Chats Stats")
        # Total
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Total Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Total Link Shared")
            st.title(num_links)

        # monthly timeline
        st.title("Monthly Timeline")
        timeline = monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["time"], timeline["message"])
        plt.xticks(rotation="vertical")
        st.pyplot(fig, width="content")

        # daily timeline
        st.title("Daily Timeline")
        timeline = daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline["only_date"], timeline["message"])
        plt.xticks(rotation="vertical")
        st.pyplot(fig, width="content")

        # activity map
        st.title("Activity Map")
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            busy_day = week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            st.pyplot(fig)

        with col2:
            st.header("Most busy Month")
            busy_day = month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(busy_day.index, busy_day.values)
            st.pyplot(fig)

        # Most Chatter User
        if selected_user == "Overall":
            st.title("Most Busy Users")

            top_busy_user, busy_user_percent = fetch_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.barh(top_busy_user.index, top_busy_user.values)
                st.pyplot(fig)

            with col2:
                st.dataframe(busy_user_percent)

        # Heatmap
        st.title("Weekly Activity Map")
        p_table = activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(p_table)
        st.pyplot(fig, width="content")

        # Word Cloud
        st.title("Wordcloud")
        df_wc = create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig, width="content")

        # Most Common Words
        most_common = most_common_words(selected_user, df)
        fig, ax = plt.subplots()

        ax.barh(most_common["word"], most_common["count"])

        st.title("Most Common Words")
        st.pyplot(fig, width="content")

        # Emoji
        emoji_df = emoji_helper(selected_user, df)

        st.title("Emoji Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            st.bar_chart(emoji_df.set_index("Emoji"))
