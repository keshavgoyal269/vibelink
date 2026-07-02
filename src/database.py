import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vibelink.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn


def init_db():
    """Creates all tables if they don't exist yet."""
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            age INTEGER,
            city TEXT,
            bio TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Activities table
    c.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            city TEXT,
            activity_date TEXT,
            activity_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Interests table (who showed interest in whose activity)
    c.execute("""
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            activity_owner_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(from_user_id, activity_id)
        )
    """)

    # Migration: add status column to interests table if it doesn't exist yet
    c.execute("PRAGMA table_info(interests)")
    existing_cols = [row[1] for row in c.fetchall()]
    if "status" not in existing_cols:
        c.execute("ALTER TABLE interests ADD COLUMN status TEXT DEFAULT 'interested'")

    # Matches table (mutual interest = match)
    c.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Messages table (chat between matched users)
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches(id)
        )
    """)

    conn.commit()
    conn.close()


# ── USER FUNCTIONS ──────────────────────────────────────────────

def create_user(name, email, password_hash, age, city, bio):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, age, city, bio) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, password_hash, age, city, bio)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # email already exists
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


# ── ACTIVITY FUNCTIONS ───────────────────────────────────────────

def create_activity(user_id, category, title, description, city, activity_date, activity_time):
    conn = get_connection()
    conn.execute(
        """INSERT INTO activities
           (user_id, category, title, description, city, activity_date, activity_time)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, category, title, description, city, activity_date, activity_time)
    )
    conn.commit()
    conn.close()


def get_activities_for_browse(current_user_id):
    """Returns activities NOT posted by the current user, not expired, that they haven't already acted on."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.*, u.name as poster_name, u.age as poster_age, u.city as poster_city, u.bio as poster_bio
        FROM activities a
        JOIN users u ON a.user_id = u.id
        WHERE a.user_id != ?
        AND a.activity_date >= date('now')
        AND a.id NOT IN (
            SELECT activity_id FROM interests WHERE from_user_id = ?
        )
        ORDER BY a.created_at DESC
    """, (current_user_id, current_user_id)).fetchall()
    conn.close()
    return rows


def get_my_activities(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM activities WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return rows


def delete_activity(activity_id, user_id):
    """Deletes an activity — only if it belongs to the requesting user."""
    conn = get_connection()
    conn.execute("DELETE FROM activities WHERE id = ? AND user_id = ?", (activity_id, user_id))
    conn.commit()
    conn.close()


# ── INTEREST & MATCHING FUNCTIONS ────────────────────────────────

def express_interest(from_user_id, activity_id, activity_owner_id, status="interested"):
    """User expresses interest OR skips an activity. Checks for mutual match only on 'interested'."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO interests (from_user_id, activity_id, activity_owner_id, status) VALUES (?, ?, ?, ?)",
            (from_user_id, activity_id, activity_owner_id, status)
        )
        conn.commit()

        if status == "interested":
            # check if activity owner also expressed genuine interest in any of from_user's activities
            mutual = conn.execute("""
                SELECT i.activity_id FROM interests i
                JOIN activities a ON i.activity_id = a.id
                WHERE i.from_user_id = ? AND a.user_id = ? AND i.status = 'interested'
            """, (activity_owner_id, from_user_id)).fetchone()

            if mutual:
                conn.execute(
                    "INSERT INTO matches (user1_id, user2_id, activity_id) VALUES (?, ?, ?)",
                    (from_user_id, activity_owner_id, activity_id)
                )
                conn.commit()
                conn.close()
                return True  # it's a match!
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return False


def get_my_matches(user_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT m.*,
               u1.name as user1_name, u2.name as user2_name,
               a.title as activity_title, a.category as activity_category
        FROM matches m
        JOIN users u1 ON m.user1_id = u1.id
        JOIN users u2 ON m.user2_id = u2.id
        JOIN activities a ON m.activity_id = a.id
        WHERE m.user1_id = ? OR m.user2_id = ?
        ORDER BY m.created_at DESC
    """, (user_id, user_id)).fetchall()
    conn.close()
    return rows


# ── CHAT FUNCTIONS ────────────────────────────────────────────────

def send_message(match_id, sender_id, content):
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (match_id, sender_id, content) VALUES (?, ?, ?)",
        (match_id, sender_id, content)
    )
    conn.commit()
    conn.close()


def get_messages(match_id):
    conn = get_connection()
    rows = conn.execute("""
        SELECT m.*, u.name as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.match_id = ?
        ORDER BY m.sent_at ASC
    """, (match_id,)).fetchall()
    conn.close()
    return rows