import time
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import os

# Import existing event system from deliverManager
from deliverManager import Event, EventArgs


class PomodoroState(Enum):
    """ポモドーロタイマーの状態"""
    STOPPED = "stopped"
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass
class Badge:
    """達成バッジのデータクラス"""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlock_date: Optional[datetime] = None


@dataclass
class PomodoroSession:
    """ポモドーロセッションの記録"""
    start_time: datetime
    end_time: Optional[datetime] = None
    completed: bool = False
    session_type: PomodoroState = PomodoroState.WORK


class PomodoroCompletedEventArgs(EventArgs):
    """ポモドーロ完了イベントの引数"""
    def __init__(self, session: PomodoroSession, xp_gained: int):
        self.session = session
        self.xp_gained = xp_gained


class LevelUpEventArgs(EventArgs):
    """レベルアップイベントの引数"""
    def __init__(self, old_level: int, new_level: int, total_xp: int):
        self.old_level = old_level
        self.new_level = new_level
        self.total_xp = total_xp


class BadgeUnlockedEventArgs(EventArgs):
    """バッジ獲得イベントの引数"""
    def __init__(self, badge: Badge):
        self.badge = badge


class PomodoroTimer:
    """ポモドーロタイマークラス"""
    
    def __init__(self, work_duration: int = 25*60, short_break_duration: int = 5*60, 
                 long_break_duration: int = 15*60, sessions_until_long_break: int = 4):
        # タイマー設定
        self.work_duration = work_duration
        self.short_break_duration = short_break_duration
        self.long_break_duration = long_break_duration
        self.sessions_until_long_break = sessions_until_long_break
        
        # 状態管理
        self.state = PomodoroState.STOPPED
        self.current_session: Optional[PomodoroSession] = None
        self.start_time: Optional[float] = None
        self.completed_work_sessions = 0
        
        # イベント
        self.on_session_started = Event()
        self.on_session_completed = Event()
        self.on_pomodoro_completed = Event()
        self.on_break_completed = Event()
        self.on_state_changed = Event()
    
    def start_work_session(self):
        """作業セッションを開始"""
        if self.state != PomodoroState.STOPPED:
            return False
        
        self.state = PomodoroState.WORK
        self.start_time = time.time()
        self.current_session = PomodoroSession(
            start_time=datetime.now(),
            session_type=PomodoroState.WORK
        )
        
        self.on_session_started.invoke(self)
        self.on_state_changed.invoke(self)
        return True
    
    def start_break(self):
        """休憩を開始"""
        if self.state != PomodoroState.STOPPED:
            return False
        
        # 長い休憩か短い休憩かを決定
        if self.completed_work_sessions % self.sessions_until_long_break == 0 and self.completed_work_sessions > 0:
            self.state = PomodoroState.LONG_BREAK
        else:
            self.state = PomodoroState.SHORT_BREAK
        
        self.start_time = time.time()
        self.current_session = PomodoroSession(
            start_time=datetime.now(),
            session_type=self.state
        )
        
        self.on_session_started.invoke(self)
        self.on_state_changed.invoke(self)
        return True
    
    def stop_session(self):
        """現在のセッションを停止"""
        if self.state == PomodoroState.STOPPED:
            return False
        
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.completed = False
        
        self.state = PomodoroState.STOPPED
        self.start_time = None
        self.current_session = None
        
        self.on_state_changed.invoke(self)
        return True
    
    def update(self):
        """タイマーの更新処理"""
        if self.state == PomodoroState.STOPPED or self.start_time is None:
            return
        
        elapsed_time = time.time() - self.start_time
        duration = self._get_current_duration()
        
        if elapsed_time >= duration:
            self._complete_current_session()
    
    def _get_current_duration(self) -> int:
        """現在のセッションの継続時間を取得"""
        if self.state == PomodoroState.WORK:
            return self.work_duration
        elif self.state == PomodoroState.SHORT_BREAK:
            return self.short_break_duration
        elif self.state == PomodoroState.LONG_BREAK:
            return self.long_break_duration
        return 0
    
    def _complete_current_session(self):
        """現在のセッションを完了"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            self.current_session.completed = True
            
            if self.state == PomodoroState.WORK:
                self.completed_work_sessions += 1
                self.on_pomodoro_completed.invoke(self, PomodoroCompletedEventArgs(self.current_session, 0))
            else:
                self.on_break_completed.invoke(self)
        
        self.state = PomodoroState.STOPPED
        self.start_time = None
        self.on_session_completed.invoke(self)
        self.on_state_changed.invoke(self)
    
    def get_remaining_time(self) -> int:
        """残り時間を秒で取得"""
        if self.state == PomodoroState.STOPPED or self.start_time is None:
            return 0
        
        elapsed_time = time.time() - self.start_time
        duration = self._get_current_duration()
        remaining = max(0, duration - elapsed_time)
        return int(remaining)
    
    def get_progress(self) -> float:
        """進捗を0.0-1.0で取得"""
        if self.state == PomodoroState.STOPPED or self.start_time is None:
            return 0.0
        
        elapsed_time = time.time() - self.start_time
        duration = self._get_current_duration()
        
        if duration == 0:
            return 1.0
        
        return min(1.0, elapsed_time / duration)


class ExperienceSystem:
    """経験値システム"""
    
    def __init__(self, data_file: str = "user_data.json"):
        self.data_file = data_file
        self.xp = 0
        self.level = 1
        self.xp_per_pomodoro = 100
        self.level_multiplier = 1.5
        
        # イベント
        self.on_xp_gained = Event()
        self.on_level_up = Event()
        
        self.load_data()
    
    def gain_xp(self, amount: int):
        """経験値を獲得"""
        old_level = self.level
        self.xp += amount
        new_level = self.calculate_level()
        
        self.on_xp_gained.invoke(self)
        
        if new_level > old_level:
            self.level = new_level
            self.on_level_up.invoke(self, LevelUpEventArgs(old_level, new_level, self.xp))
        
        self.save_data()
    
    def calculate_level(self) -> int:
        """総経験値からレベルを計算"""
        level = 1
        xp_required = 1000  # レベル2に必要なXP
        
        while self.xp >= xp_required:
            level += 1
            xp_required = int(xp_required * self.level_multiplier)
        
        return level
    
    def get_xp_for_next_level(self) -> int:
        """次のレベルに必要な経験値を取得"""
        current_level_xp = self.get_xp_for_level(self.level)
        next_level_xp = self.get_xp_for_level(self.level + 1)
        return next_level_xp - self.xp
    
    def get_xp_for_level(self, level: int) -> int:
        """指定レベルに必要な総経験値を計算"""
        if level <= 1:
            return 0
        
        total_xp = 0
        xp_required = 1000
        
        for i in range(2, level + 1):
            total_xp += xp_required
            xp_required = int(xp_required * self.level_multiplier)
        
        return total_xp
    
    def load_data(self):
        """データをファイルから読み込み"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.xp = data.get('xp', 0)
                    self.level = data.get('level', 1)
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
    
    def save_data(self):
        """データをファイルに保存"""
        try:
            data = {
                'xp': self.xp,
                'level': self.level,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"データ保存エラー: {e}")


class BadgeManager:
    """バッジ管理システム"""
    
    def __init__(self, data_file: str = "badges_data.json"):
        self.data_file = data_file
        self.badges: Dict[str, Badge] = {}
        self.on_badge_unlocked = Event()
        
        self._initialize_badges()
        self.load_data()
    
    def _initialize_badges(self):
        """バッジを初期化"""
        badge_definitions = [
            ("first_pomodoro", "初回完了", "初めてのポモドーロを完了", "🍅"),
            ("early_bird", "早起き", "午前6時前にポモドーロを開始", "🌅"),
            ("night_owl", "夜更かし", "午後10時以降にポモドーロを開始", "🦉"),
            ("streak_3", "3日連続", "3日連続でポモドーロを実行", "🔥"),
            ("streak_7", "1週間連続", "7日連続でポモドーロを実行", "⭐"),
            ("streak_30", "1ヶ月連続", "30日連続でポモドーロを実行", "🏆"),
            ("productive_5", "生産的な5回", "1日に5回のポモドーロを完了", "💪"),
            ("productive_10", "生産的な10回", "1日に10回のポモドーロを完了", "🚀"),
            ("century", "100回達成", "累計100回のポモドーロを完了", "💯"),
            ("marathon", "マラソン", "累計500回のポモドーロを完了", "🏃"),
        ]
        
        for badge_id, name, description, icon in badge_definitions:
            self.badges[badge_id] = Badge(badge_id, name, description, icon)
    
    def check_badge_conditions(self, stats: 'StatisticsManager'):
        """バッジの獲得条件をチェック"""
        # 初回完了バッジ
        if stats.get_total_completed_pomodoros() >= 1:
            self._unlock_badge("first_pomodoro")
        
        # ストリークバッジ
        current_streak = stats.get_current_streak()
        if current_streak >= 3:
            self._unlock_badge("streak_3")
        if current_streak >= 7:
            self._unlock_badge("streak_7")
        if current_streak >= 30:
            self._unlock_badge("streak_30")
        
        # 生産的バッジ
        today_count = stats.get_daily_pomodoros(date.today())
        if today_count >= 5:
            self._unlock_badge("productive_5")
        if today_count >= 10:
            self._unlock_badge("productive_10")
        
        # 累計バッジ
        total = stats.get_total_completed_pomodoros()
        if total >= 100:
            self._unlock_badge("century")
        if total >= 500:
            self._unlock_badge("marathon")
        
        # 時間帯バッジ
        now = datetime.now()
        if now.hour < 6:
            self._unlock_badge("early_bird")
        elif now.hour >= 22:
            self._unlock_badge("night_owl")
    
    def _unlock_badge(self, badge_id: str):
        """バッジを獲得"""
        if badge_id in self.badges and not self.badges[badge_id].unlocked:
            self.badges[badge_id].unlocked = True
            self.badges[badge_id].unlock_date = datetime.now()
            self.on_badge_unlocked.invoke(self, BadgeUnlockedEventArgs(self.badges[badge_id]))
            self.save_data()
    
    def get_unlocked_badges(self) -> List[Badge]:
        """獲得済みバッジのリストを取得"""
        return [badge for badge in self.badges.values() if badge.unlocked]
    
    def get_progress(self) -> float:
        """バッジ獲得進捗を取得"""
        total = len(self.badges)
        unlocked = len(self.get_unlocked_badges())
        return unlocked / total if total > 0 else 0.0
    
    def load_data(self):
        """バッジデータを読み込み"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for badge_id, badge_data in data.items():
                        if badge_id in self.badges:
                            self.badges[badge_id].unlocked = badge_data.get('unlocked', False)
                            unlock_date_str = badge_data.get('unlock_date')
                            if unlock_date_str:
                                self.badges[badge_id].unlock_date = datetime.fromisoformat(unlock_date_str)
        except Exception as e:
            print(f"バッジデータ読み込みエラー: {e}")
    
    def save_data(self):
        """バッジデータを保存"""
        try:
            data = {}
            for badge_id, badge in self.badges.items():
                data[badge_id] = {
                    'unlocked': badge.unlocked,
                    'unlock_date': badge.unlock_date.isoformat() if badge.unlock_date else None
                }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"バッジデータ保存エラー: {e}")


class StatisticsManager:
    """統計管理システム"""
    
    def __init__(self, data_file: str = "statistics_data.json"):
        self.data_file = data_file
        self.sessions: List[PomodoroSession] = []
        self.daily_stats: Dict[str, int] = {}  # 日付文字列 -> 完了数
        
        self.load_data()
    
    def add_session(self, session: PomodoroSession):
        """セッションを記録"""
        if session.completed and session.session_type == PomodoroState.WORK:
            self.sessions.append(session)
            date_str = session.start_time.date().isoformat()
            self.daily_stats[date_str] = self.daily_stats.get(date_str, 0) + 1
            self.save_data()
    
    def get_total_completed_pomodoros(self) -> int:
        """総完了ポモドーロ数を取得"""
        return len([s for s in self.sessions if s.completed and s.session_type == PomodoroState.WORK])
    
    def get_daily_pomodoros(self, target_date: date) -> int:
        """指定日のポモドーロ完了数を取得"""
        date_str = target_date.isoformat()
        return self.daily_stats.get(date_str, 0)
    
    def get_weekly_stats(self, target_date: date = None) -> Dict[str, int]:
        """週間統計を取得"""
        if target_date is None:
            target_date = date.today()
        
        # その週の月曜日を取得
        monday = target_date - timedelta(days=target_date.weekday())
        weekly_stats = {}
        
        for i in range(7):
            day = monday + timedelta(days=i)
            day_str = day.isoformat()
            weekly_stats[day_str] = self.daily_stats.get(day_str, 0)
        
        return weekly_stats
    
    def get_monthly_stats(self, target_date: date = None) -> Dict[str, int]:
        """月間統計を取得"""
        if target_date is None:
            target_date = date.today()
        
        # その月の1日から月末まで
        first_day = target_date.replace(day=1)
        if target_date.month == 12:
            last_day = first_day.replace(year=target_date.year + 1, month=1) - timedelta(days=1)
        else:
            last_day = first_day.replace(month=target_date.month + 1) - timedelta(days=1)
        
        monthly_stats = {}
        current_day = first_day
        
        while current_day <= last_day:
            day_str = current_day.isoformat()
            monthly_stats[day_str] = self.daily_stats.get(day_str, 0)
            current_day += timedelta(days=1)
        
        return monthly_stats
    
    def get_current_streak(self) -> int:
        """現在の連続日数を取得"""
        today = date.today()
        streak = 0
        current_date = today
        
        while True:
            if self.get_daily_pomodoros(current_date) > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def get_completion_rate(self, days: int = 30) -> float:
        """指定期間の完了率を取得"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        total_days = 0
        completed_days = 0
        
        current_date = start_date
        while current_date <= end_date:
            total_days += 1
            if self.get_daily_pomodoros(current_date) > 0:
                completed_days += 1
            current_date += timedelta(days=1)
        
        return completed_days / total_days if total_days > 0 else 0.0
    
    def get_average_focus_time(self, days: int = 30) -> float:
        """指定期間の平均集中時間を取得（分）"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        relevant_sessions = [
            s for s in self.sessions 
            if s.completed and s.session_type == PomodoroState.WORK 
            and start_date <= s.start_time.date() <= end_date
        ]
        
        if not relevant_sessions:
            return 0.0
        
        total_minutes = len(relevant_sessions) * 25  # 1ポモドーロ = 25分
        total_days = (end_date - start_date).days + 1
        
        return total_minutes / total_days
    
    def load_data(self):
        """統計データを読み込み"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # セッションデータを復元
                    session_data = data.get('sessions', [])
                    self.sessions = []
                    for s_data in session_data:
                        session = PomodoroSession(
                            start_time=datetime.fromisoformat(s_data['start_time']),
                            session_type=PomodoroState(s_data['session_type']),
                            completed=s_data.get('completed', False)
                        )
                        if s_data.get('end_time'):
                            session.end_time = datetime.fromisoformat(s_data['end_time'])
                        self.sessions.append(session)
                    
                    # 日別統計を復元
                    self.daily_stats = data.get('daily_stats', {})
        except Exception as e:
            print(f"統計データ読み込みエラー: {e}")
    
    def save_data(self):
        """統計データを保存"""
        try:
            session_data = []
            for session in self.sessions:
                s_data = {
                    'start_time': session.start_time.isoformat(),
                    'session_type': session.session_type.value,
                    'completed': session.completed
                }
                if session.end_time:
                    s_data['end_time'] = session.end_time.isoformat()
                session_data.append(s_data)
            
            data = {
                'sessions': session_data,
                'daily_stats': self.daily_stats,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"統計データ保存エラー: {e}")


class StreakManager:
    """ストリーク管理システム"""
    
    def __init__(self, stats_manager: StatisticsManager):
        self.stats_manager = stats_manager
    
    def get_current_streak(self) -> int:
        """現在の連続日数を取得"""
        return self.stats_manager.get_current_streak()
    
    def get_longest_streak(self) -> int:
        """最長連続日数を取得"""
        max_streak = 0
        current_streak = 0
        
        # 統計データから日付順に処理
        sorted_dates = sorted(self.stats_manager.daily_stats.keys())
        
        previous_date = None
        for date_str in sorted_dates:
            current_date = date.fromisoformat(date_str)
            count = self.stats_manager.daily_stats[date_str]
            
            if count > 0:
                if previous_date is None or current_date == previous_date + timedelta(days=1):
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
                previous_date = current_date
            else:
                current_streak = 0
                previous_date = None
        
        return max_streak
    
    def get_streak_for_period(self, start_date: date, end_date: date) -> int:
        """指定期間内での最長ストリークを取得"""
        streak = 0
        current_date = start_date
        
        while current_date <= end_date:
            if self.stats_manager.get_daily_pomodoros(current_date) > 0:
                streak += 1
            else:
                break
            current_date += timedelta(days=1)
        
        return streak


class PomodoroGameSystem:
    """ポモドーロタイマーのゲーミフィケーションシステム統合クラス"""
    
    def __init__(self):
        # コンポーネントの初期化
        self.timer = PomodoroTimer()
        self.experience = ExperienceSystem()
        self.statistics = StatisticsManager()
        self.badges = BadgeManager()
        self.streaks = StreakManager(self.statistics)
        
        # イベントハンドラーの設定
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """イベントハンドラーを設定"""
        # ポモドーロ完了時
        self.timer.on_pomodoro_completed.add_handler(self._on_pomodoro_completed)
        
        # レベルアップ時
        self.experience.on_level_up.add_handler(self._on_level_up)
        
        # バッジ獲得時
        self.badges.on_badge_unlocked.add_handler(self._on_badge_unlocked)
    
    def _on_pomodoro_completed(self, sender, args: PomodoroCompletedEventArgs):
        """ポモドーロ完了時の処理"""
        # 統計に記録
        self.statistics.add_session(args.session)
        
        # 経験値を付与
        xp_gained = self.experience.xp_per_pomodoro
        self.experience.gain_xp(xp_gained)
        
        # バッジ条件をチェック
        self.badges.check_badge_conditions(self.statistics)
        
        # 完了メッセージ
        print(f"🍅 ポモドーロ完了！ +{xp_gained} XP")
        print(f"📊 現在の統計: レベル {self.experience.level}, 総完了数 {self.statistics.get_total_completed_pomodoros()}")
        print(f"🔥 現在のストリーク: {self.streaks.get_current_streak()}日")
    
    def _on_level_up(self, sender, args: LevelUpEventArgs):
        """レベルアップ時の処理"""
        print(f"🎉 レベルアップ！ {args.old_level} → {args.new_level}")
        print(f"✨ 総経験値: {args.total_xp}")
    
    def _on_badge_unlocked(self, sender, args: BadgeUnlockedEventArgs):
        """バッジ獲得時の処理"""
        badge = args.badge
        print(f"🏆 新しいバッジ獲得: {badge.icon} {badge.name}")
        print(f"📝 {badge.description}")
    
    def start_work_session(self):
        """作業セッションを開始"""
        if self.timer.start_work_session():
            print("🚀 作業セッション開始！25分間集中しましょう。")
            return True
        return False
    
    def start_break(self):
        """休憩を開始"""
        if self.timer.start_break():
            break_type = "長い休憩" if self.timer.state == PomodoroState.LONG_BREAK else "短い休憩"
            duration = self.timer.long_break_duration if self.timer.state == PomodoroState.LONG_BREAK else self.timer.short_break_duration
            print(f"☕ {break_type}開始！{duration//60}分間リラックスしましょう。")
            return True
        return False
    
    def stop_session(self):
        """現在のセッションを停止"""
        if self.timer.stop_session():
            print("⏹️ セッションを停止しました。")
            return True
        return False
    
    def update(self):
        """システム全体の更新処理"""
        self.timer.update()
    
    def display_status(self):
        """現在の状態を表示"""
        print("\n" + "="*50)
        print("🍅 ポモドーロタイマー ステータス")
        print("="*50)
        
        # タイマー状態
        state_text = {
            PomodoroState.STOPPED: "停止中",
            PomodoroState.WORK: "作業中",
            PomodoroState.SHORT_BREAK: "短い休憩中",
            PomodoroState.LONG_BREAK: "長い休憩中"
        }
        print(f"📱 状態: {state_text[self.timer.state]}")
        
        if self.timer.state != PomodoroState.STOPPED:
            remaining = self.timer.get_remaining_time()
            minutes = remaining // 60
            seconds = remaining % 60
            progress = self.timer.get_progress() * 100
            print(f"⏰ 残り時間: {minutes:02d}:{seconds:02d}")
            print(f"📈 進捗: {progress:.1f}%")
        
        # 経験値とレベル
        print(f"\n🌟 レベル: {self.experience.level}")
        print(f"✨ 経験値: {self.experience.xp}")
        print(f"🎯 次のレベルまで: {self.experience.get_xp_for_next_level()} XP")
        
        # 統計
        total_pomodoros = self.statistics.get_total_completed_pomodoros()
        current_streak = self.streaks.get_current_streak()
        longest_streak = self.streaks.get_longest_streak()
        completion_rate = self.statistics.get_completion_rate(30) * 100
        avg_focus = self.statistics.get_average_focus_time(30)
        
        print(f"\n📊 統計 (過去30日)")
        print(f"🍅 総ポモドーロ数: {total_pomodoros}")
        print(f"🔥 現在のストリーク: {current_streak}日")
        print(f"🏆 最長ストリーク: {longest_streak}日")
        print(f"📈 完了率: {completion_rate:.1f}%")
        print(f"🎯 平均集中時間: {avg_focus:.1f}分/日")
        
        # バッジ
        unlocked_badges = self.badges.get_unlocked_badges()
        badge_progress = self.badges.get_progress() * 100
        print(f"\n🏆 バッジ ({len(unlocked_badges)}/{len(self.badges.badges)} - {badge_progress:.1f}%)")
        
        if unlocked_badges:
            for badge in unlocked_badges[-3:]:  # 最新の3つを表示
                print(f"  {badge.icon} {badge.name}")
        
        print("="*50)
    
    def display_weekly_chart(self):
        """週間チャートを表示"""
        weekly_stats = self.statistics.get_weekly_stats()
        print("\n📊 今週のポモドーロ完了数")
        print("月  火  水  木  金  土  日")
        
        values = list(weekly_stats.values())
        max_val = max(values) if values else 0
        
        # 簡単な棒グラフ表示
        for row in range(max(3, max_val), -1, -1):
            line = ""
            for val in values:
                if val >= row:
                    line += "██ "
                else:
                    line += "   "
            print(line)
        
        # 数値表示
        print(" ".join([f"{v:2d}" for v in values]))