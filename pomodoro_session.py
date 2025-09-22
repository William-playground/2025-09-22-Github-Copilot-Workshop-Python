import sqlite3
import time
from datetime import datetime, date
from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PomodoroSession:
    """Pomodoro session data model"""
    id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: int = 25  # Default Pomodoro duration
    completed: bool = False
    task_description: str = ""
    created_at: Optional[datetime] = None


class PomodoroDatabase:
    """Database manager for Pomodoro sessions"""
    
    def __init__(self, db_path: str = "pomodoro_sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_minutes INTEGER NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    task_description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save_session(self, session: PomodoroSession) -> int:
        """Save a Pomodoro session to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO pomodoro_sessions 
                (start_time, end_time, duration_minutes, completed, task_description)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session.start_time.isoformat() if session.start_time else None,
                session.end_time.isoformat() if session.end_time else None,
                session.duration_minutes,
                session.completed,
                session.task_description
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_today_sessions(self) -> List[PomodoroSession]:
        """Get all sessions for today"""
        today = date.today()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM pomodoro_sessions 
                WHERE date(created_at) = ?
                ORDER BY created_at DESC
            """, (today.isoformat(),))
            
            sessions = []
            for row in cursor.fetchall():
                session = PomodoroSession(
                    id=row['id'],
                    start_time=datetime.fromisoformat(row['start_time']) if row['start_time'] else None,
                    end_time=datetime.fromisoformat(row['end_time']) if row['end_time'] else None,
                    duration_minutes=row['duration_minutes'],
                    completed=bool(row['completed']),
                    task_description=row['task_description'] or "",
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                sessions.append(session)
            
            return sessions
    
    def get_today_stats(self) -> Dict:
        """Get statistics for today's sessions"""
        sessions = self.get_today_sessions()
        
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.completed])
        total_minutes = sum(s.duration_minutes for s in sessions if s.completed)
        
        return {
            "date": date.today().isoformat(),
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "incomplete_sessions": total_sessions - completed_sessions,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2) if total_minutes > 0 else 0,
            "sessions": [
                {
                    "id": s.id,
                    "start_time": s.start_time.isoformat() if s.start_time else None,
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "duration_minutes": s.duration_minutes,
                    "completed": s.completed,
                    "task_description": s.task_description
                }
                for s in sessions
            ]
        }


class PomodoroTimer:
    """Pomodoro timer manager"""
    
    def __init__(self, db: PomodoroDatabase):
        self.db = db
        self.current_session: Optional[PomodoroSession] = None
        self.is_running = False
    
    def start_session(self, duration_minutes: int = 25, task_description: str = "") -> PomodoroSession:
        """Start a new Pomodoro session"""
        if self.is_running:
            raise ValueError("A session is already running")
        
        session = PomodoroSession(
            start_time=datetime.now(),
            duration_minutes=duration_minutes,
            task_description=task_description,
            completed=False
        )
        
        self.current_session = session
        self.is_running = True
        return session
    
    def complete_session(self) -> Optional[PomodoroSession]:
        """Complete the current session and save to database"""
        if not self.is_running or not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.completed = True
        
        # Save to database
        session_id = self.db.save_session(self.current_session)
        self.current_session.id = session_id
        
        # Reset state
        completed_session = self.current_session
        self.current_session = None
        self.is_running = False
        
        return completed_session
    
    def cancel_session(self) -> Optional[PomodoroSession]:
        """Cancel the current session (save as incomplete)"""
        if not self.is_running or not self.current_session:
            return None
        
        self.current_session.end_time = datetime.now()
        self.current_session.completed = False
        
        # Save to database as incomplete
        session_id = self.db.save_session(self.current_session)
        self.current_session.id = session_id
        
        # Reset state
        cancelled_session = self.current_session
        self.current_session = None
        self.is_running = False
        
        return cancelled_session
    
    def get_current_session(self) -> Optional[PomodoroSession]:
        """Get the current running session"""
        return self.current_session
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in minutes for current session"""
        if not self.current_session or not self.current_session.start_time:
            return 0.0
        
        elapsed = datetime.now() - self.current_session.start_time
        return elapsed.total_seconds() / 60.0
    
    def get_remaining_time(self) -> float:
        """Get remaining time in minutes for current session"""
        if not self.current_session:
            return 0.0
        
        elapsed = self.get_elapsed_time()
        remaining = self.current_session.duration_minutes - elapsed
        return max(0.0, remaining)
    
    def is_session_complete(self) -> bool:
        """Check if current session time has elapsed"""
        return self.get_remaining_time() <= 0.0


# Singleton instance for global access
_pomodoro_db = None
_pomodoro_timer = None


def get_pomodoro_db() -> PomodoroDatabase:
    """Get singleton database instance"""
    global _pomodoro_db
    if _pomodoro_db is None:
        _pomodoro_db = PomodoroDatabase()
    return _pomodoro_db


def get_pomodoro_timer() -> PomodoroTimer:
    """Get singleton timer instance"""
    global _pomodoro_timer
    if _pomodoro_timer is None:
        _pomodoro_timer = PomodoroTimer(get_pomodoro_db())
    return _pomodoro_timer


# Test the functionality
if __name__ == "__main__":
    # Initialize database and timer
    db = get_pomodoro_db()
    timer = get_pomodoro_timer()
    
    print("Pomodoro Session System Test")
    print("=" * 40)
    
    # Start a session
    session = timer.start_session(duration_minutes=1, task_description="Test task")
    print(f"Started session: {session.task_description}")
    print(f"Duration: {session.duration_minutes} minutes")
    
    # Simulate some work time
    time.sleep(2)
    print(f"Elapsed time: {timer.get_elapsed_time():.2f} minutes")
    print(f"Remaining time: {timer.get_remaining_time():.2f} minutes")
    
    # Complete the session
    completed = timer.complete_session()
    print(f"Completed session ID: {completed.id}")
    
    # Get today's statistics
    stats = db.get_today_stats()
    print("\nToday's Statistics:")
    print(f"Total sessions: {stats['total_sessions']}")
    print(f"Completed sessions: {stats['completed_sessions']}")
    print(f"Total minutes: {stats['total_minutes']}")