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

# Page configuration
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global custom styling (WhatsApp modern aesthetic)
st.markdown(
    """
    <style>
    /* Main container and font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Header hero styling */
    .hero-banner {
        background: linear-gradient(135deg, #075E54 0%, #128C7E 60%, #25D366 100%);
        padding: 1.6rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(7, 94, 84, 0.25);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 1rem;
        opacity: 0.92;
        margin-top: 6px;
        margin-bottom: 0;
        color: #E8F5E9;
    }
    .user-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.22);
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        margin-top: 10px;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }

    /* Metric Cards */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.2rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: var(--background-color, #ffffff);
        border: 1px solid rgba(18, 140, 126, 0.16);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(7, 94, 84, 0.12);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #128C7E, #25D366);
    }
    .metric-icon {
        font-size: 1.7rem;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #075E54;
        line-height: 1.2;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-top: 0.3rem;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #075E54;
        margin-top: 1.6rem;
        margin-bottom: 0.85rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .chart-card {
        background: var(--background-color, #ffffff);
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.2rem;
    }

    /* Landing Card for empty state */
    .empty-state {
        background: #ffffff;
        border: 2px dashed #CBD5E1;
        border-radius: 20px;
        padding: 3rem 2rem;
        text-align: center;
        margin-top: 2rem;
    }
    .empty-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
    }
    .feature-pill {
        display: inline-block;
        background: #E8F5E9;
        color: #075E54;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Matplotlib global theme setup
plt.rcParams["figure.facecolor"] = "none"
plt.rcParams["axes.facecolor"] = "none"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["text.color"] = "#1E293B"
plt.rcParams["axes.labelcolor"] = "#475569"
plt.rcParams["xtick.color"] = "#64748B"
plt.rcParams["ytick.color"] = "#64748B"

# Sidebar
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem;">
        <span style="font-size: 2.2rem;">💬</span>
        <div>
            <h2 style="margin: 0; font-size: 1.35rem; color: #075E54; font-weight: 700;">WhatsApp</h2>
            <p style="margin: 0; font-size: 0.85rem; color: #64748B;">Chat Analytics Suite</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.sidebar.file_uploader(
    "Choose exported chat (.txt)",
    type=["txt"],
    help="Export chat from WhatsApp without media and upload here",
)

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")

    df = preprocessor(data)

    user_list = df["user"].unique().tolist()
    if "group_notification" in user_list:
        user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

    analyze_button = st.sidebar.button("📊 Show Analysis", use_container_width=True)

    if analyze_button or "analyzed" in st.session_state:
        st.session_state["analyzed"] = True

        # Header Hero Banner
        st.markdown(
            f"""
            <div class="hero-banner">
                <div class="hero-title">
                    <span>💬 WhatsApp Chat Insights</span>
                </div>
                <div class="hero-subtitle">Comprehensive analytical breakdown of messaging patterns, user activity, and text semantics.</div>
                <div class="user-badge">Scope: {selected_user}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 1. Top Stat Cards
        num_messages, words, num_media_messages, num_links = fetch_stats(
            selected_user, df
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">💬</div>
                    <div class="metric-value">{num_messages:,}</div>
                    <div class="metric-title">Total Messages</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">📝</div>
                    <div class="metric-value">{words:,}</div>
                    <div class="metric-title">Total Words</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">📷</div>
                    <div class="metric-value">{num_media_messages:,}</div>
                    <div class="metric-title">Media Shared</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-value">{num_links:,}</div>
                    <div class="metric-title">Links Shared</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # 2. Activity Timelines (Tabbed for clean, compact space)
        st.markdown(
            '<div class="section-header">📈 Activity Timelines Over Time</div>',
            unsafe_allow_html=True,
        )
        tab_month, tab_daily = st.tabs(["📅 Monthly Timeline", "📆 Daily Timeline"])

        with tab_month:
            timeline_month = monthly_timeline(selected_user, df)
            fig_m, ax_m = plt.subplots(figsize=(10, 3.8))
            ax_m.plot(
                timeline_month["time"],
                timeline_month["message"],
                color="#128C7E",
                marker="o",
                linewidth=2.2,
                markersize=4.5,
                markerfacecolor="#075E54",
            )
            ax_m.fill_between(
                timeline_month["time"],
                timeline_month["message"],
                color="#128C7E",
                alpha=0.15,
            )
            ax_m.set_ylabel("Message Count", fontsize=10, fontweight="bold")
            ax_m.grid(True, linestyle="--", alpha=0.3, color="#94A3B8")
            plt.xticks(rotation=45, ha="right", fontsize=9)
            sns.despine(top=True, right=True)
            plt.tight_layout()
            st.pyplot(fig_m, use_container_width=True)
            plt.close(fig_m)

        with tab_daily:
            timeline_day = daily_timeline(selected_user, df)
            fig_d, ax_d = plt.subplots(figsize=(10, 3.8))
            ax_d.plot(
                timeline_day["only_date"],
                timeline_day["message"],
                color="#25D366",
                linewidth=1.8,
            )
            ax_d.fill_between(
                timeline_day["only_date"],
                timeline_day["message"],
                color="#25D366",
                alpha=0.15,
            )
            ax_d.set_ylabel("Message Count", fontsize=10, fontweight="bold")
            ax_d.grid(True, linestyle="--", alpha=0.3, color="#94A3B8")
            plt.xticks(rotation=45, ha="right", fontsize=9)
            sns.despine(top=True, right=True)
            plt.tight_layout()
            st.pyplot(fig_d, use_container_width=True)
            plt.close(fig_d)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # 3. Activity Patterns (Day of Week & Month of Year Side-by-Side)
        st.markdown(
            '<div class="section-header">🗓️ Messaging Activity Patterns</div>',
            unsafe_allow_html=True,
        )
        col_act1, col_act2 = st.columns(2)

        with col_act1:
            st.markdown(
                "**Most Active Days of the Week**",
                help="Total messages sent per day of the week",
            )
            busy_day = week_activity_map(selected_user, df)
            fig_w, ax_w = plt.subplots(figsize=(6, 3.6))
            bars_w = ax_w.bar(
                busy_day.index,
                busy_day.values,
                color="#128C7E",
                width=0.55,
                edgecolor="none",
                zorder=3,
            )
            ax_w.bar_label(
                bars_w, padding=3, fontsize=9, color="#1E293B", fontweight="bold"
            )
            ax_w.set_ylabel("Messages", fontsize=9, fontweight="bold")
            ax_w.grid(axis="y", linestyle="--", alpha=0.35, color="#94A3B8", zorder=0)
            plt.xticks(rotation=30, ha="right", fontsize=9)
            sns.despine(top=True, right=True)
            plt.tight_layout()
            st.pyplot(fig_w, use_container_width=True)
            plt.close(fig_w)

        with col_act2:
            st.markdown(
                "**Most Active Months**",
                help="Total messages sent per month",
            )
            busy_month = month_activity_map(selected_user, df)
            fig_mo, ax_mo = plt.subplots(figsize=(6, 3.6))
            bars_mo = ax_mo.barh(
                busy_month.index,
                busy_month.values,
                color="#25D366",
                height=0.55,
                edgecolor="none",
                zorder=3,
            )
            ax_mo.bar_label(
                bars_mo, padding=3, fontsize=9, color="#1E293B", fontweight="bold"
            )
            ax_mo.set_xlabel("Messages", fontsize=9, fontweight="bold")
            ax_mo.invert_yaxis()
            ax_mo.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8", zorder=0)
            sns.despine(top=True, right=True)
            plt.tight_layout()
            st.pyplot(fig_mo, use_container_width=True)
            plt.close(fig_mo)

        # 4. User Contribution & Ranking (Overall only)
        if selected_user == "Overall":
            st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
            st.markdown(
                '<div class="section-header">👥 Member Participation & Engagement</div>',
                unsafe_allow_html=True,
            )
            top_busy_user, busy_user_percent = fetch_busy_users(df)

            col_usr1, col_usr2 = st.columns([1.1, 0.9])

            with col_usr1:
                st.markdown("**Top 5 Most Active Members**")
                fig_u, ax_u = plt.subplots(figsize=(6, 3.6))
                colors_u = ["#075E54", "#128C7E", "#25D366", "#34B7F1", "#64748B"]
                bars_u = ax_u.barh(
                    top_busy_user.index,
                    top_busy_user.values,
                    color=colors_u[: len(top_busy_user)],
                    height=0.55,
                    edgecolor="none",
                    zorder=3,
                )
                ax_u.bar_label(
                    bars_u, padding=4, fontsize=9, color="#1E293B", fontweight="bold"
                )
                ax_u.invert_yaxis()
                ax_u.set_xlabel("Total Messages", fontsize=9, fontweight="bold")
                ax_u.grid(
                    axis="x", linestyle="--", alpha=0.35, color="#94A3B8", zorder=0
                )
                sns.despine(top=True, right=True)
                plt.tight_layout()
                st.pyplot(fig_u, use_container_width=True)
                plt.close(fig_u)

            with col_usr2:
                st.markdown("**Contribution Breakdown**")
                st.dataframe(
                    busy_user_percent,
                    use_container_width=True,
                    height=280,
                    column_config={
                        "name": st.column_config.TextColumn("Member Name"),
                        "percent(%)": st.column_config.ProgressColumn(
                            "Share of Chat",
                            format="%.2f%%",
                            min_value=0,
                            max_value=100,
                        ),
                    },
                )

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # 5. Weekly Activity Heatmap
        st.markdown(
            '<div class="section-header">🕒 Weekly Activity Heatmap (Peak Messaging Hours)</div>',
            unsafe_allow_html=True,
        )
        p_table = activity_heatmap(selected_user, df)
        fig_h, ax_h = plt.subplots(figsize=(11, 4.2))
        sns.heatmap(
            p_table,
            cmap="YlGnBu",
            linewidths=0.6,
            linecolor="#F8FAFC",
            ax=ax_h,
            cbar_kws={"label": "Message Volume", "shrink": 0.8},
        )
        ax_h.set_xlabel("Time Period", fontsize=10, fontweight="bold")
        ax_h.set_ylabel("Day of Week", fontsize=10, fontweight="bold")
        plt.xticks(rotation=45, ha="right", fontsize=8.5)
        plt.yticks(rotation=0, fontsize=9)
        plt.tight_layout()
        st.pyplot(fig_h, use_container_width=True)
        plt.close(fig_h)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # 6. Text Semantics: Word Cloud & Most Common Words Side-by-Side
        st.markdown(
            '<div class="section-header">🔤 Vocabulary & Frequent Words</div>',
            unsafe_allow_html=True,
        )
        col_wc, col_cw = st.columns([1, 1])

        with col_wc:
            st.markdown("**Word Cloud**")
            df_wc = create_wordcloud(selected_user, df)
            fig_wc, ax_wc = plt.subplots(figsize=(5.5, 4.8))
            ax_wc.imshow(df_wc, interpolation="bilinear")
            ax_wc.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig_wc, use_container_width=True)
            plt.close(fig_wc)

        with col_cw:
            st.markdown("**Top 20 Most Frequent Words**")
            most_common = most_common_words(selected_user, df)
            fig_mc, ax_mc = plt.subplots(figsize=(5.5, 4.8))
            bars_mc = ax_mc.barh(
                most_common["word"],
                most_common["count"],
                color="#128C7E",
                height=0.65,
                edgecolor="none",
                zorder=3,
            )
            ax_mc.bar_label(bars_mc, padding=3, fontsize=8, color="#1E293B")
            ax_mc.invert_yaxis()
            ax_mc.set_xlabel("Occurrences", fontsize=9, fontweight="bold")
            ax_mc.grid(axis="x", linestyle="--", alpha=0.35, color="#94A3B8", zorder=0)
            sns.despine(top=True, right=True)
            plt.tight_layout()
            st.pyplot(fig_mc, use_container_width=True)
            plt.close(fig_mc)

        st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

        # 7. Emoji Analysis
        st.markdown(
            '<div class="section-header">😃 Emoji Sentiment & Usage</div>',
            unsafe_allow_html=True,
        )
        emoji_df = emoji_helper(selected_user, df)

        if not emoji_df.empty:
            col_em1, col_em2 = st.columns([1, 1])
            with col_em1:
                st.markdown("**Emoji Frequency Table**")
                st.dataframe(
                    emoji_df,
                    use_container_width=True,
                    height=360,
                    column_config={
                        "Emoji": st.column_config.TextColumn("Emoji"),
                        "Count": st.column_config.NumberColumn("Usage Count"),
                    },
                )
            with col_em2:
                st.markdown("**Top 10 Most Used Emojis**")
                top_emojis = emoji_df.head(10)
                st.bar_chart(
                    top_emojis.set_index("Emoji"),
                    color="#25D366",
                    horizontal=True,
                    height=360,
                )
        else:
            st.info("No emojis detected in the messages for this selection.")

else:
    # Empty State - Welcome Banner with Instructions
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-icon">📱</div>
            <h2 style="color: #075E54; font-weight: 700; margin-bottom: 0.5rem;">WhatsApp Chat Analyzer</h2>
            <p style="color: #64748B; font-size: 1.05rem; max-width: 600px; margin: 0 auto 1.5rem auto;">
                Uncover powerful insights, messaging habits, peak hours, member rankings, and emoji usage from your WhatsApp group or individual chats.
            </p>
            <div style="margin-bottom: 1.8rem;">
                <span class="feature-pill">📊 Activity Metrics</span>
                <span class="feature-pill">📈 Monthly & Daily Timelines</span>
                <span class="feature-pill">🕒 Weekly Heatmaps</span>
                <span class="feature-pill">👥 Member Rankings</span>
                <span class="feature-pill">🔤 Word Clouds</span>
                <span class="feature-pill">😃 Emoji Analytics</span>
            </div>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.2rem; max-width: 520px; margin: 0 auto; text-align: left;">
                <p style="margin: 0 0 8px 0; font-weight: 600; color: #075E54; font-size: 0.95rem;">💡 How to get started:</p>
                <ol style="margin: 0; padding-left: 1.2rem; color: #475569; font-size: 0.9rem; line-height: 1.6;">
                    <li>Open WhatsApp on your phone or web.</li>
                    <li>Go to the chat > tap <strong>More</strong> > <strong>Export chat</strong>.</li>
                    <li>Choose <strong>Without Media</strong>.</li>
                    <li>Upload the generated <code>.txt</code> file in the sidebar to view instant analytics.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
