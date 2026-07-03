import streamlit as st
from streamlit_autorefresh import st_autorefresh
import sys, os, uuid

sys.path.insert(0, os.path.dirname(__file__))

from src.database import (
    init_db, get_activities_for_browse, get_my_activities,
    create_activity, get_messages, send_message, get_connection,
    create_user, get_user_by_email
)
from src.matching import handle_interest, get_matches_with_details, CATEGORIES, CATEGORY_EMOJI

# ── PAGE CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="VibeLink",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL STYLES ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

#MainMenu, footer, header { visibility: hidden; }

.nav-bar {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding: 14px 32px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24px;
    border-radius: 0 0 16px 16px;
}
.nav-logo {
    font-size: 26px;
    font-weight: 800;
    background: linear-gradient(90deg, #f953c6, #b91d73);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nav-user { color: rgba(255,255,255,0.7); font-size: 14px; }

.activity-card {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    transition: transform 0.2s;
}
.activity-card:hover {
    transform: translateY(-3px);
    border-color: rgba(249,83,198,0.4);
}
.activity-emoji { font-size: 42px; margin-bottom: 8px; }
.activity-category {
    background: linear-gradient(90deg, #f953c6, #b91d73);
    color: white;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
.activity-title { color: white; font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.activity-meta { color: rgba(255,255,255,0.55); font-size: 13px; margin-bottom: 10px; }
.activity-desc { color: rgba(255,255,255,0.8); font-size: 14px; line-height: 1.5; }
.poster-info {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid rgba(255,255,255,0.1);
    color: rgba(255,255,255,0.6);
    font-size: 13px;
}

.match-card {
    background: linear-gradient(135deg, rgba(249,83,198,0.15), rgba(185,29,115,0.1));
    border: 1px solid rgba(249,83,198,0.3);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 16px;
}
.match-name { color: white; font-size: 18px; font-weight: 700; }
.match-activity { color: rgba(249,83,198,0.9); font-size: 13px; font-weight: 600; }

.bubble-sent {
    background: linear-gradient(135deg, #f953c6, #b91d73);
    color: white;
    padding: 10px 16px;
    border-radius: 18px 18px 4px 18px;
    margin: 6px 0;
    max-width: 70%;
    margin-left: auto;
    font-size: 14px;
}
.bubble-received {
    background: rgba(255,255,255,0.1);
    color: white;
    padding: 10px 16px;
    border-radius: 18px 18px 18px 4px;
    margin: 6px 0;
    max-width: 70%;
    font-size: 14px;
}
.bubble-name { font-size: 11px; color: rgba(255,255,255,0.45); margin-bottom: 2px; }
.bubble-time { font-size: 10px; color: rgba(255,255,255,0.35); margin-top: 3px; }

.section-title { color: white; font-size: 24px; font-weight: 800; margin-bottom: 20px; }
.section-sub { color: rgba(255,255,255,0.5); font-size: 14px; margin-top: -16px; margin-bottom: 24px; }

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: rgba(255,255,255,0.6) !important;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #f953c6, #b91d73) !important;
    color: white !important;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Poppins', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(249,83,198,0.4) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: white !important;
}

.empty-state { text-align: center; padding: 60px 20px; }
.empty-state-icon { font-size: 64px; margin-bottom: 16px; }
.empty-state-text { font-size: 18px; font-weight: 600; color: rgba(255,255,255,0.5); }

.match-banner {
    background: linear-gradient(135deg, #f953c6, #b91d73);
    border-radius: 20px;
    padding: 20px 28px;
    text-align: center;
    color: white;
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 20px;
}

.edit-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 24px;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── INIT DATABASE ─────────────────────────────────────────────────
init_db()

# ── AUTO SESSION: create a guest user automatically ───────────────
def ensure_session():
    """
    Every visitor gets auto-assigned a guest identity the first time
    they open the app — no login required.
    """
    if "user_id" not in st.session_state:
        # generate a unique guest email for this browser session
        guest_id = str(uuid.uuid4())[:8]
        guest_email = f"guest_{guest_id}@vibelink.app"
        guest_name = f"Guest_{guest_id[:4].upper()}"

        # create the account in the DB
        import bcrypt
        password_hash = bcrypt.hashpw(guest_id.encode(), bcrypt.gensalt()).decode()
        create_user(guest_name, guest_email, password_hash, 25, "Your City", "VibeLink visitor")

        user = get_user_by_email(guest_email)
        st.session_state["user_id"] = user["id"]
        st.session_state["user_name"] = guest_name
        st.session_state["is_guest"] = True


ensure_session()
user_id = st.session_state["user_id"]


def render_navbar():
    name = st.session_state.get("user_name", "")
    st.markdown(f"""
    <div class="nav-bar">
        <div class="nav-logo">⚡ VibeLink</div>
        <div class="nav-user">👋 Hey, {name}!</div>
    </div>
    """, unsafe_allow_html=True)


# ── SEED SAMPLE DATA ─────────────────────────────────────────────
def seed_sample_data():
    """Add sample users and activities so the app never looks empty."""
    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE email = 'priya@vibelink.app'").fetchone()
    if not existing:
        import bcrypt
        users = [
            ("Priya Sharma", "priya@vibelink.app", "Mumbai", 23,
             "Badminton lover, coffee addict, avid hiker. Let's do something fun!"),
            ("Arjun Mehta", "arjun@vibelink.app", "Delhi", 26,
             "Pickleball enthusiast and weekend runner. Always up for new activities!"),
            ("Aisha Khan", "aisha@vibelink.app", "Bangalore", 24,
             "Yoga in the morning, trivia nights on weekends. Love meeting new people."),
            ("Rohan Verma", "rohan@vibelink.app", "Kota", 21,
             "Tennis and cycling are my thing. Also love a good coffee chat."),
        ]
        for u in users:
            ph = bcrypt.hashpw(b"demo123", bcrypt.gensalt()).decode()
            conn.execute("""
                INSERT OR IGNORE INTO users (name, email, password_hash, age, city, bio)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (u[0], u[1], ph, u[3], u[2], u[4]))
        conn.commit()

        sample_acts = [
            ("priya@vibelink.app", "Badminton", "Casual badminton at Shivaji Park",
             "All levels welcome, just bring good energy!", "Mumbai", "2026-07-10", "07:00:00"),
            ("priya@vibelink.app", "Coffee", "Sunday morning coffee catch-up",
             "Looking for someone to chat over great coffee ☕", "Mumbai", "2026-07-06", "10:30:00"),
            ("arjun@vibelink.app", "Pickleball", "Pickleball at NSCI Dome",
             "Beginner friendly! Rackets available.", "Delhi", "2026-07-08", "08:00:00"),
            ("arjun@vibelink.app", "Running / Jogging", "Evening run at Lodhi Garden",
             "5km easy pace, everyone welcome 🏃", "Delhi", "2026-07-05", "18:00:00"),
            ("aisha@vibelink.app", "Yoga / Gym", "Morning yoga at Cubbon Park",
             "Relaxed session, all levels. Bring your mat!", "Bangalore", "2026-07-07", "06:30:00"),
            ("aisha@vibelink.app", "Trivia Night", "Weekly trivia at Social",
             "Teams of 2-4, prizes for winners 🎯", "Bangalore", "2026-07-09", "19:00:00"),
            ("rohan@vibelink.app", "Tennis", "Tennis at District Park",
             "Intermediate level, friendly match", "Kota", "2026-07-11", "07:30:00"),
            ("rohan@vibelink.app", "Hiking", "Weekend hike at Mukundra Hills",
             "Easy trail, stunning views. Carpooling available!", "Kota", "2026-07-12", "06:00:00"),
        ]

        for act in sample_acts:
            user_row = conn.execute("SELECT id FROM users WHERE email=?", (act[0],)).fetchone()
            if user_row:
                conn.execute("""
                    INSERT INTO activities
                    (user_id, category, title, description, city, activity_date, activity_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_row["id"], act[1], act[2], act[3], act[4], act[5], act[6]))
        conn.commit()
    conn.close()


seed_sample_data()

# ══════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════
render_navbar()

tab_browse, tab_post, tab_matches, tab_chat, tab_profile = st.tabs([
    "🔍  Discover", "➕  Post Activity", "💞  My Matches", "💬  Chat", "👤  Profile"
])

# ── DISCOVER ─────────────────────────────────────────────────────
with tab_browse:
    st.markdown('<div class="section-title">Discover Activities</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Find someone to do things with — tap Interested to connect</div>', unsafe_allow_html=True)

    filter_options = ["All"] + CATEGORIES
    selected_filter = st.selectbox("Filter", filter_options, key="browse_filter", label_visibility="collapsed")

    activities = get_activities_for_browse(user_id)
    if selected_filter != "All":
        activities = [a for a in activities if a["category"] == selected_filter]

    if not activities:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🎯</div>
            <div class="empty-state-text">No activities yet — post one to get started!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, activity in enumerate(activities):
            emoji = CATEGORY_EMOJI.get(activity["category"], "✨")
            with cols[i % 2]:
                st.markdown(f"""
                <div class="activity-card">
                    <div class="activity-emoji">{emoji}</div>
                    <div class="activity-category">{activity['category']}</div>
                    <div class="activity-title">{activity['title']}</div>
                    <div class="activity-meta">
                        📍 {activity['city']} &nbsp;·&nbsp;
                        📅 {activity['activity_date']} &nbsp;·&nbsp;
                        🕐 {activity['activity_time']}
                    </div>
                    <div class="activity-desc">{activity['description'] or ''}</div>
                    <div class="poster-info">
                        Posted by <strong style="color:white;">{activity['poster_name']}</strong>,
                        {activity['poster_age']} · {activity['poster_city']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_int, col_skip = st.columns(2)
                with col_int:
                    if st.button("💫 Interested", key=f"int_{activity['id']}", use_container_width=True, type="primary"):
                        matched = handle_interest(user_id, activity["id"], activity["user_id"])
                        if matched:
                            st.markdown('<div class="match-banner">🎉 It\'s a Match! Check your Matches tab!</div>', unsafe_allow_html=True)
                        else:
                            st.success("Interest sent!")
                        st.rerun()
                with col_skip:
                    if st.button("✕ Skip", key=f"skip_{activity['id']}", use_container_width=True):
                        from src.database import express_interest
                        express_interest(user_id, activity["id"], activity["user_id"])
                        st.rerun()

# ── POST ACTIVITY ─────────────────────────────────────────────────
with tab_post:
    st.markdown('<div class="section-title">Post an Activity</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Tell people what you want to do and find your match</div>', unsafe_allow_html=True)

    with st.form("post_activity_form", clear_on_submit=True):
        category = st.selectbox("Activity type", CATEGORIES,
                                 format_func=lambda x: f"{CATEGORY_EMOJI.get(x,'✨')} {x}")
        title = st.text_input("Title", placeholder="e.g. 'Casual badminton in Lajpat Nagar'")
        description = st.text_area("Description", placeholder="Skill level, vibe, what to expect...", height=100)
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("City", placeholder="Delhi")
        with col2:
            activity_date = st.date_input("Date")
        with col3:
            activity_time = st.time_input("Time")
        if st.form_submit_button("Post Activity 🚀", use_container_width=True, type="primary"):
            if title and city:
                create_activity(user_id, category, title, description,
                                city, str(activity_date), str(activity_time))
                st.success("Posted! People can now discover and match with you. 🎉")
            else:
                st.warning("Please add a title and city.")

    my_activities = get_my_activities(user_id)
    if my_activities:
        st.markdown("---")
        st.markdown('<div class="section-title" style="font-size:18px;">Your Posted Activities</div>', unsafe_allow_html=True)
        for act in my_activities:
            emoji = CATEGORY_EMOJI.get(act["category"], "✨")
            st.markdown(f"""
            <div class="activity-card">
                <div class="activity-emoji">{emoji}</div>
                <div class="activity-category">{act['category']}</div>
                <div class="activity-title">{act['title']}</div>
                <div class="activity-meta">📍 {act['city']} &nbsp;·&nbsp; 📅 {act['activity_date']} &nbsp;·&nbsp; 🕐 {act['activity_time']}</div>
                <div class="activity-desc">{act['description'] or ''}</div>
            </div>
            """, unsafe_allow_html=True)

# ── MATCHES ───────────────────────────────────────────────────────
with tab_matches:
    st.markdown('<div class="section-title">Your Matches 💞</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">People who share your vibe</div>', unsafe_allow_html=True)

    matches = get_matches_with_details(user_id)
    if not matches:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💞</div>
            <div class="empty-state-text">No matches yet — go show some interest in activities!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for match in matches:
            emoji = CATEGORY_EMOJI.get(match["activity_category"], "✨")
            st.markdown(f"""
            <div class="match-card">
                <div class="match-name">⚡ {match['other_name']}, {match['other_age']}</div>
                <div style="color:rgba(255,255,255,0.55); font-size:13px; margin:4px 0;">📍 {match['other_city']}</div>
                <div class="match-activity">{emoji} Matched on: {match['activity_title']}</div>
                <div style="color:rgba(255,255,255,0.45); font-size:12px; margin-top:8px;">{match['other_bio'] or ''}</div>
                <div style="color:rgba(255,255,255,0.3); font-size:11px; margin-top:10px;">Matched {match['matched_at'][:10]}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"💬 Chat with {match['other_name']}", key=f"chat_btn_{match['match_id']}", type="primary"):
                st.session_state["active_chat_match_id"] = match["match_id"]
                st.session_state["active_chat_name"] = match["other_name"]
                st.rerun()

# ── CHAT ─────────────────────────────────────────────────────────
with tab_chat:
    st_autorefresh(interval=5000, key="chat_refresh")
    st.markdown('<div class="section-title">Messages 💬</div>', unsafe_allow_html=True)

    matches = get_matches_with_details(user_id)
    if not matches:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">💬</div>
            <div class="empty-state-text">Match with someone to start chatting!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        match_names = {m["match_id"]: f"{CATEGORY_EMOJI.get(m['activity_category'],'✨')} {m['other_name']}" for m in matches}
        active_match_id = st.session_state.get("active_chat_match_id", matches[0]["match_id"])
        active_match_name = st.session_state.get("active_chat_name", matches[0]["other_name"])

        col_list, col_msgs = st.columns([1, 2.5])
        with col_list:
            st.markdown("**Conversations**")
            for match in matches:
                label = match_names[match["match_id"]]
                is_active = match["match_id"] == active_match_id
                if st.button(label, key=f"conv_{match['match_id']}",
                              use_container_width=True,
                              type="primary" if is_active else "secondary"):
                    st.session_state["active_chat_match_id"] = match["match_id"]
                    st.session_state["active_chat_name"] = match["other_name"]
                    st.rerun()

        with col_msgs:
            st.markdown(f"**Chat with {active_match_name}**")
            messages = get_messages(active_match_id)
            chat_html = '<div style="max-height:400px; overflow-y:auto; padding:10px;">'
            for msg in messages:
                is_mine = msg["sender_id"] == user_id
                time_str = msg["sent_at"][11:16] if msg["sent_at"] else ""
                if is_mine:
                    chat_html += f"""
                    <div style="text-align:right;">
                        <div class="bubble-sent">{msg['content']}</div>
                        <div class="bubble-time" style="text-align:right;">{time_str}</div>
                    </div>"""
                else:
                    chat_html += f"""
                    <div style="text-align:left;">
                        <div class="bubble-name">{msg['sender_name']}</div>
                        <div class="bubble-received">{msg['content']}</div>
                        <div class="bubble-time">{time_str}</div>
                    </div>"""
            chat_html += "</div>"
            st.markdown(chat_html, unsafe_allow_html=True)

            with st.form(f"chat_form_{active_match_id}", clear_on_submit=True):
                col_input, col_send = st.columns([4, 1])
                with col_input:
                    msg_text = st.text_input("", placeholder="Type a message...", label_visibility="collapsed")
                with col_send:
                    if st.form_submit_button("Send ➜", use_container_width=True, type="primary"):
                        if msg_text.strip():
                            send_message(active_match_id, user_id, msg_text.strip())
                            st.rerun()

# ── PROFILE ───────────────────────────────────────────────────────
with tab_profile:
    from src.database import get_user_by_id
    user = get_user_by_id(user_id)

    st.markdown('<div class="section-title">Your Profile 👤</div>', unsafe_allow_html=True)

    if user:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class="match-card" style="text-align:center; padding:32px;">
                <div style="font-size:64px;">👤</div>
                <div class="match-name" style="font-size:22px; margin-top:12px;">{user['name']}</div>
                <div style="color:rgba(255,255,255,0.55); margin-top:6px;">📍 {user['city']}</div>
                <div style="color:rgba(255,255,255,0.55);">🎂 {user['age']} years old</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="activity-card">
                <div style="color:rgba(255,255,255,0.5); font-size:13px; margin-bottom:4px;">BIO</div>
                <div style="color:white; font-size:15px; line-height:1.6;">{user['bio'] or 'No bio yet.'}</div>
                <div style="margin-top:20px; color:rgba(255,255,255,0.5); font-size:13px;">MEMBER SINCE</div>
                <div style="color:white; font-size:14px;">{user['created_at'][:10]}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── EDIT PROFILE ──────────────────────────────────────────
        st.markdown('<div class="edit-card">', unsafe_allow_html=True)
        st.markdown("### ✏️ Edit Your Profile")
        with st.form("edit_profile_form"):
            new_name = st.text_input("Name", value=user["name"] or "")
            new_bio = st.text_area("Bio", value=user["bio"] or "", height=100)
            col_a, col_b = st.columns(2)
            with col_a:
                new_city = st.text_input("City", value=user["city"] or "")
            with col_b:
                new_age = st.number_input("Age", min_value=18, max_value=80,
                                           value=int(user["age"]) if user["age"] else 25)
            if st.form_submit_button("Save Changes ✅", use_container_width=True, type="primary"):
                conn = get_connection()
                conn.execute(
                    "UPDATE users SET name=?, bio=?, city=?, age=? WHERE id=?",
                    (new_name, new_bio, new_city, new_age, user_id)
                )
                conn.commit()
                conn.close()
                st.session_state["user_name"] = new_name
                st.success("Profile updated! ✅")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)