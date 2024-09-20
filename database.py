import sqlite3
from contextlib import closing

from config import database_name


# Database setup
def init_db():
    with sqlite3.Connection(database_name) as conn:
        with closing(conn.cursor()) as cursor:

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    name TEXT,
                    username TEXT,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_hours INT DEFAULT 0
                )
            ''')

            # Create the study_hours table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_hours (
                    hour_id INTEGER PRIMARY KEY,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    hours INT,
                    user_id BIGINT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            # Create the points_awards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points_awards (
                    point_id INTEGER PRIMARY KEY,
                    giver TEXT,
                    points INT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_id BIGINT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')

            conn.commit()


def get_user_id(username: str = None):
    with sqlite3.Connection(database_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
    return result


def insert_ignore(user_id: int, name: str, username: str = None):
    try:
        with sqlite3.Connection(database_name) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('INSERT OR IGNORE INTO users(user_id, name, username) VALUES (?, ?, ?)',
                               (user_id, name, username or 'null'))
                conn.commit()
        return True

    except sqlite3.OperationalError as e:
        print(f"Operational Error (possibly connection issue): {e}")
        return False
    except sqlite3.IntegrityError as e:
        print(f"Integrity Error (possibly constraint violation): {e}")
        return False
    except sqlite3.DataError as e:
        print(f"Data Error (invalid data type): {e}")
        return False
    except sqlite3.Error as e:
        print(f"General SQLite error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def get_daily():
    with sqlite3.Connection(database_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT 
                    u.name,
                    u.username,
                    COALESCE(p.total_points_today, 0) AS total_points_today,
                    COALESCE(s.total_hours_today, 0) AS total_hours_today
                FROM 
                    users u
                LEFT JOIN 
                    (SELECT user_id, SUM(points) as total_points_today 
                    FROM points_awards 
                    WHERE date(date) = date('now')
                    GROUP BY user_id) p ON u.user_id = p.user_id
                LEFT JOIN 
                    (SELECT user_id, SUM(hours) as total_hours_today 
                    FROM study_hours 
                    WHERE date(date) = date('now')
                    GROUP BY user_id) s ON u.user_id = s.user_id
                ORDER BY 
                    total_hours_today DESC
            ''')

            results = cursor.fetchall()
    return results


def get_month():
    with sqlite3.Connection(database_name) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                SELECT 
                    u.name,
                    u.username,
                    COALESCE(p.total_points_month, 0) AS total_points_month,
                    COALESCE(s.total_hours_month, 0) AS total_hours_month
                FROM 
                    users u
                LEFT JOIN 
                    (SELECT user_id, SUM(points) as total_points_month 
                    FROM points_awards 
                    WHERE date >= date('now', 'start of month')
                    GROUP BY user_id) p ON u.user_id = p.user_id
                LEFT JOIN 
                    (SELECT user_id, SUM(hours) as total_hours_month 
                    FROM study_hours 
                    WHERE date >= date('now', 'start of month')
                    GROUP BY user_id) s ON u.user_id = s.user_id
                ORDER BY 
                    total_points_month DESC
            ''')

            results = cursor.fetchall()
    return results
