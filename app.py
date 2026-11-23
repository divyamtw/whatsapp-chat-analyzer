import streamlit as st
import matplotlib.pyplot as plt

from preprocessor import preprocessor
from helper import fetch_stats, fetch_busy_users, create_wordcloud, most_common_words

st.set_page_config(layout="wide")
st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    # st.text(data)

    df = preprocessor(data)

    st.title("Whatsapp Chats")
    st.dataframe(df)

    user_list = df["user"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, words, num_media_messages, num_links = fetch_stats(
            selected_user, df
        )

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

        # Most Chatter User
        if selected_user == "Overall":
            st.title("Most Busy Users")

            top_busy_user, busy_user_percent = fetch_busy_users(df)
            fig, ax = plt.subplots()

            b_user1, b_user2 = st.columns(2)

            with b_user1:
                ax.barh(top_busy_user.index, top_busy_user.values)
                # plt.xticks(rotation="vertical")
                st.pyplot(fig)

            with b_user2:
                st.dataframe(busy_user_percent)

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
        # plt.xticks(rotation="vertical")

        st.title("Most Common Words")
        st.pyplot(fig, width="content")
