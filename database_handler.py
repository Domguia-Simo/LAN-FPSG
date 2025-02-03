import sqlite3
import time
import os
from settings import DB_PATH

class DatabaseHandler:
    def __init__(self):
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(db_dir, 'game_stats.db')
        
        # Check if database exists
        is_new_db = not os.path.exists(self.db_path)
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        if is_new_db:
            self.create_tables()
        else:
            self.update_schema()
            
        print("Database initialized")

    def create_tables(self):
        """Create fresh tables with current schema"""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            );
            
            CREATE TABLE IF NOT EXISTS game_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                start_time INTEGER,
                end_time INTEGER NULL,
                total_kills INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS player_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                player_name TEXT,
                health INTEGER,
                kills INTEGER,
                timestamp INTEGER,
                FOREIGN KEY(session_id) REFERENCES game_sessions(id)
            );
            
            INSERT INTO schema_version (version) VALUES (1);
        ''')
        self.conn.commit()
        print("Created new database with current schema")

    def update_schema(self):
        """Update existing database schema if needed"""
        try:
            # Check if schema_version table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'")
            if not self.cursor.fetchone():
                # No schema version table, assume old version
                # Add the missing columns
                self.cursor.executescript('''
                    ALTER TABLE game_sessions ADD COLUMN total_kills INTEGER DEFAULT 0;
                    CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
                    INSERT INTO schema_version (version) VALUES (1);
                ''')
                self.conn.commit()
                print("Updated database schema")
            
            # Check for end_time column
            self.cursor.execute("PRAGMA table_info(game_sessions)")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            if 'end_time' not in columns:
                self.cursor.execute('ALTER TABLE game_sessions ADD COLUMN end_time INTEGER NULL')
                self.conn.commit()
                print("Added end_time column")
        except sqlite3.OperationalError as e:
            print(f"Schema update error: {e}")
            # If error occurs, recreate the tables
            self.cursor.executescript('''
                DROP TABLE IF EXISTS game_sessions;
                DROP TABLE IF EXISTS player_stats;
                DROP TABLE IF EXISTS schema_version;
            ''')
            self.create_tables()

    def start_new_session(self, player_name):
        """Start a new game session"""
        self.cursor.execute('''
            INSERT INTO game_sessions (player_name, start_time, total_kills)
            VALUES (?, ?, ?)
        ''', (player_name, time.time(), 0))
        self.conn.commit()
        self.current_session_id = self.cursor.lastrowid
        print(f"New session started: {self.current_session_id} for player: {player_name}")

    def save_player_stats(self, player_name, health, kills):
        """Save stats for current session"""
        if not self.current_session_id:
            self.start_new_session(player_name)
            
        try:
            self.cursor.execute('''
                INSERT INTO player_stats (session_id, player_name, health, kills, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (self.current_session_id, player_name, health, kills, time.time()))
            
            # Update total kills for the session
            self.cursor.execute('''
                UPDATE game_sessions 
                SET total_kills = ?
                WHERE id = ?
            ''', (kills, self.current_session_id))
            
            self.conn.commit()
            print(f"Stats saved - Player: {player_name}, Health: {health}, Kills: {kills}")
        except Exception as e:
            print(f"Error saving stats: {e}")

    def get_player_stats(self, player_name):
        self.cursor.execute('''
            SELECT * FROM player_stats 
            WHERE player_name = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (player_name,))
        return self.cursor.fetchone()

    def get_high_scores(self, limit=10):
        """Get top players by kills"""
        self.cursor.execute('''
            SELECT player_name, MAX(total_kills) as max_kills 
            FROM game_sessions 
            GROUP BY player_name 
            ORDER BY max_kills DESC 
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()

    def get_player_history(self, player_name, limit=10):
        """Get recent games for a player"""
        self.cursor.execute('''
            SELECT health, kills, timestamp 
            FROM player_stats 
            WHERE player_name = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (player_name, limit))
        return self.cursor.fetchall()

    def get_total_kills(self, player_name):
        """Get highest kill count from any single session"""
        self.cursor.execute('''
            SELECT MAX(kills)
            FROM player_stats 
            WHERE player_name = ?
        ''', (player_name,))
        return self.cursor.fetchone()[0] or 0

    def get_all_time_kills(self, player_name):
        """Get total kills across all sessions"""
        try:
            self.cursor.execute('''
                SELECT MAX(total_kills) 
                FROM game_sessions 
                WHERE player_name = ?
            ''', (player_name,))
            result = self.cursor.fetchone()[0]
            total_kills = result if result is not None else 0
            print(f"All-time kills for {player_name}: {total_kills}")
            return total_kills
        except Exception as e:
            print(f"Error getting all-time kills: {e}")
            return 0

    def get_session_stats(self, player_name):
        """Get number of sessions and best session"""
        self.cursor.execute('''
            SELECT COUNT(*), MAX(total_kills)
            FROM game_sessions
            WHERE player_name = ?
        ''', (player_name,))
        return self.cursor.fetchone()

    def close(self):
        """Close database connection safely"""
        try:
            if hasattr(self, 'current_session_id'):
                self.cursor.execute('''
                    UPDATE game_sessions 
                    SET end_time = ?, total_kills = (
                        SELECT MAX(kills) FROM player_stats 
                        WHERE session_id = ?
                    )
                    WHERE id = ?
                ''', (int(time.time()), self.current_session_id, self.current_session_id))
                self.conn.commit()
        except Exception as e:
            print(f"Error closing database: {e}")
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()
                print("Database connection closed")
