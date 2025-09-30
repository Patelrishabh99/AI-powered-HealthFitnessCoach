import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Custom CSS for better visibility
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Inter', sans-serif;
}

.progress-header {
    background: rgba(255, 255, 255, 0.95);
    padding: 3rem;
    border-radius: 20px;
    color: #2D3748;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    border: 2px solid rgba(255,255,255,0.3);
}

.metric-card {
    background: rgba(255, 255, 255, 0.98);
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
}

.leaderboard-container {
    background: rgba(255, 255, 255, 0.98);
    padding: 2rem;
    border-radius: 20px;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    border: 2px solid rgba(255,255,255,0.3);
}

.leaderboard-item {
    background: rgba(255, 255, 255, 0.95);
    padding: 1.2rem;
    margin: 0.8rem 0;
    border-radius: 12px;
    border-left: 4px solid #4ECDC4;
    transition: all 0.3s ease;
    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

.leaderboard-item:hover {
    transform: translateX(5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.rank-1 { 
    border-left: 6px solid #FFD700 !important;
    background: linear-gradient(135deg, #FFF9C4, #FFFFFF) !important;
    font-weight: bold;
}
.rank-2 { 
    border-left: 6px solid #C0C0C0 !important;
    background: linear-gradient(135deg, #F5F5F5, #FFFFFF) !important;
}
.rank-3 { 
    border-left: 6px solid #CD7F32 !important;
    background: linear-gradient(135deg, #E8D2B0, #FFFFFF) !important;
}

.user-highlight {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    font-weight: bold;
    border-left: 6px solid #FF6B6B !important;
}

.leaderboard-username {
    font-weight: 600;
    font-size: 1.1rem;
    color: #2D3748;
    margin: 0;
}

.leaderboard-stats {
    font-size: 0.9rem;
    color: #4A5568;
    margin: 0.2rem 0 0 0;
}

.chart-container {
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

/* Improved text contrast */
.stats-number {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2D3748;
    margin: 0;
}

.stats-label {
    font-size: 1rem;
    color: #4A5568;
    margin: 0;
}

/* Better contrast for all text elements */
h1, h2, h3, h4, h5, h6 {
    color: #2D3748 !important;
}

p, div, span {
    color: #4A5568 !important;
}

/* Specific fix for leaderboard text */
.leaderboard-item .leaderboard-username {
    color: #2D3748 !important;
    font-weight: 600;
}

.leaderboard-item .leaderboard-stats {
    color: #4A5568 !important;
}

/* Ensure Plotly charts have white background */
.js-plotly-plot .plotly .modebar {
    background: rgba(255,255,255,0.9) !important;
}
</style>
""", unsafe_allow_html=True)


# Database functions
def get_user_progress():
    conn = sqlite3.connect("data/user_logs.db")
    query = """
    SELECT username, exercise, SUM(reps) as total_reps, 
           COUNT(*) as sessions, MAX(date) as last_activity,
           AVG(reps) as avg_reps_per_session
    FROM user_progress 
    GROUP BY username, exercise
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_leaderboard():
    conn = sqlite3.connect("data/user_logs.db")
    df = pd.read_sql_query("""
        SELECT username, SUM(reps) as total_reps, 
               COUNT(DISTINCT date) as active_days,
               MAX(date) as last_active
        FROM user_progress 
        GROUP BY username 
        ORDER BY total_reps DESC
    """, conn)
    conn.close()
    return df


def get_user_stats(username):
    conn = sqlite3.connect("data/user_logs.db")

    # Total stats
    total_query = """
    SELECT SUM(reps) as total_reps, COUNT(DISTINCT date) as total_days,
           COUNT(*) as total_sessions, MIN(date) as join_date
    FROM user_progress 
    WHERE username = ?
    """
    total_stats = pd.read_sql_query(total_query, conn, params=(username,))

    # Exercise distribution
    exercise_query = """
    SELECT exercise, SUM(reps) as exercise_reps, COUNT(*) as sessions
    FROM user_progress 
    WHERE username = ?
    GROUP BY exercise
    ORDER BY exercise_reps DESC
    """
    exercise_stats = pd.read_sql_query(exercise_query, conn, params=(username,))

    # Weekly progress
    weekly_query = """
    SELECT date, SUM(reps) as daily_reps
    FROM user_progress 
    WHERE username = ?
    GROUP BY date
    ORDER BY date
    """
    weekly_stats = pd.read_sql_query(weekly_query, conn, params=(username,))

    conn.close()
    return total_stats, exercise_stats, weekly_stats


# Page configuration
st.set_page_config(page_title="Progress Dashboard", layout="wide")

# Header Section with improved contrast
st.markdown("""
<div class="progress-header">
    <h1 style="color: #2D3748; margin: 0; font-size: 3rem;">📊 Fitness Progress Dashboard</h1>
    <p style="color: #4A5568; font-size: 1.2rem; margin: 1rem 0;">Track your journey and compete with friends!</p>
</div>
""", unsafe_allow_html=True)

# Get data from database
progress_df = get_user_progress()
leaderboard_df = get_leaderboard()

# User selection in sidebar with better visibility
st.sidebar.markdown("""
<style>
.sidebar-content {
    background: rgba(255,255,255,0.95) !important;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("### 👤 Select User Profile")
username = st.sidebar.selectbox(
    "Choose User:",
    options=["All Users"] + leaderboard_df['username'].tolist(),
    index=0
)

# Main Metrics Overview with better contrast
if username == "All Users":
    # Overall platform stats
    total_reps = leaderboard_df['total_reps'].sum()
    total_users = len(leaderboard_df)
    total_days = leaderboard_df['active_days'].sum()
    avg_reps_per_user = leaderboard_df['total_reps'].mean()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #667eea; margin: 0;">🏋️ Total Reps</h3>
            <p class="stats-number">{total_reps:,}</p>
            <p class="stats-label">Across all users</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ff6b6b; margin: 0;">👥 Active Users</h3>
            <p class="stats-number">{total_users}</p>
            <p class="stats-label">Fitness community</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #4ecdc4; margin: 0;">📅 Active Days</h3>
            <p class="stats-number">{total_days}</p>
            <p class="stats-label">Total workout days</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #96CEB4; margin: 0;">📊 Avg per User</h3>
            <p class="stats-number">{avg_reps_per_user:.0f}</p>
            <p class="stats-label">Reps per user</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Individual user stats
    total_stats, exercise_stats, weekly_stats = get_user_stats(username)

    if not total_stats.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #667eea; margin: 0;">🏋️ Total Reps</h3>
                <p class="stats-number">{total_stats.iloc[0]['total_reps']:,}</p>
                <p class="stats-label">Your fitness journey</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #ff6b6b; margin: 0;">📅 Active Days</h3>
                <p class="stats-number">{total_stats.iloc[0]['total_days']}</p>
                <p class="stats-label">Workout sessions</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4ecdc4; margin: 0;">🔥 Total Sessions</h3>
                <p class="stats-number">{total_stats.iloc[0]['total_sessions']}</p>
                <p class="stats-label">Exercise sessions</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            join_date = total_stats.iloc[0]['join_date']
            days_active = (datetime.now() - datetime.strptime(join_date, '%Y-%m-%d %H:%M:%S')).days
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #96CEB4; margin: 0;">⏱️ Days Active</h3>
                <p class="stats-number">{days_active}</p>
                <p class="stats-label">Since {join_date[:10]}</p>
            </div>
            """, unsafe_allow_html=True)

# Leaderboard Section with FIXED VISIBILITY
st.markdown("""
<div class="leaderboard-container">
    <h2 style="color: #2D3748; text-align: center; margin-bottom: 2rem;">🏆 Community Leaderboard</h2>
""", unsafe_allow_html=True)

# Enhanced leaderboard with clear visibility
leaderboard_df['rank'] = range(1, len(leaderboard_df) + 1)

for _, row in leaderboard_df.iterrows():
    rank_class = ""
    if row['rank'] == 1:
        rank_class = "rank-1"
        emoji = "👑"
    elif row['rank'] == 2:
        rank_class = "rank-2"
        emoji = "🥈"
    elif row['rank'] == 3:
        rank_class = "rank-3"
        emoji = "🥉"
    else:
        emoji = "⭐"

    user_class = "user-highlight" if row['username'] == username else ""

    st.markdown(f"""
    <div class="leaderboard-item {rank_class} {user_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span class="leaderboard-username">{emoji} #{row['rank']} {row['username']}</span>
            <span style="font-size: 1.1rem; font-weight: 600; color: #667eea;">{row['total_reps']:,} reps</span>
        </div>
        <div class="leaderboard-stats">
            📅 {row['active_days']} active days • 🕐 Last: {row['last_active'][:10]}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # Close leaderboard-container

# Charts Section with better visibility
st.markdown("""
<div class="chart-container">
    <h2 style="color: #2D3748; margin-bottom: 2rem;">📈 Progress Analytics</h2>
""", unsafe_allow_html=True)

if username != "All Users" and not weekly_stats.empty:
    col1, col2 = st.columns(2)

    with col1:
        # Weekly Progress Chart
        weekly_stats['date'] = pd.to_datetime(weekly_stats['date'])
        fig_weekly = px.line(weekly_stats, x='date', y='daily_reps',
                             title=f'{username} - Daily Progress',
                             labels={'daily_reps': 'Reps per Day', 'date': 'Date'})
        fig_weekly.update_layout(
            plot_bgcolor='rgba(255,255,255,0.9)',
            paper_bgcolor='rgba(255,255,255,0.9)',
            font=dict(color='#2D3748')
        )
        st.plotly_chart(fig_weekly, use_container_width=True)

    with col2:
        # Exercise Distribution
        if not exercise_stats.empty:
            fig_dist = px.pie(exercise_stats, values='exercise_reps', names='exercise',
                              title=f'{username} - Exercise Distribution',
                              hole=0.4)
            fig_dist.update_layout(
                plot_bgcolor='rgba(255,255,255,0.9)',
                paper_bgcolor='rgba(255,255,255,0.9)',
                font=dict(color='#2D3748')
            )
            st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)  # Close chart-container

# Exercise Breakdown with better visibility
st.markdown("""
<div class="chart-container">
    <h2 style="color: #2D3748; margin-bottom: 2rem;">💪 Exercise Performance</h2>
""", unsafe_allow_html=True)

if username == "All Users":
    # Overall exercise stats
    exercise_summary = progress_df.groupby('exercise').agg({
        'total_reps': 'sum',
        'sessions': 'sum',
        'username': 'nunique'
    }).reset_index()

    for _, exercise in exercise_summary.iterrows():
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(f"🏋️ {exercise['exercise']} - Total Reps", f"{exercise['total_reps']:,}")

        with col2:
            st.metric("📊 Total Sessions", exercise['sessions'])

        with col3:
            st.metric("👥 Active Users", exercise['username'])

        with col4:
            avg_reps = exercise['total_reps'] / exercise['sessions'] if exercise['sessions'] > 0 else 0
            st.metric("📈 Avg per Session", f"{avg_reps:.1f}")

else:
    # Individual user exercise stats
    if not exercise_stats.empty:
        for _, exercise in exercise_stats.iterrows():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(f"🏋️ {exercise['exercise']} - Total Reps", f"{exercise['exercise_reps']:,}")

            with col2:
                st.metric("📊 Sessions Completed", exercise['sessions'])

            with col3:
                avg_reps = exercise['exercise_reps'] / exercise['sessions'] if exercise['sessions'] > 0 else 0
                st.metric("📈 Avg per Session", f"{avg_reps:.1f}")

st.markdown("</div>", unsafe_allow_html=True)  # Close exercise-container

# Final motivational section
st.markdown("""
<div class="progress-header" style="text-align: center;">
    <h2 style="color: #2D3748; margin-bottom: 1rem;">🚀 Keep Going!</h2>
    <p style="color: #4A5568; font-size: 1.1rem;">Every rep counts toward your fitness goals. Stay consistent and amazing results will follow!</p>
</div>
""", unsafe_allow_html=True)