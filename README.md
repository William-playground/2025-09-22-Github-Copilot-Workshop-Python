# カスタマイズ可能なポモドーロタイマー
# Customizable Pomodoro Timer

ワークショップの手順：https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0

## 🍅 概要 / Overview

個人の好みに合わせた利用体験を実現するカスタマイズ可能なポモドーロタイマーです。

A customizable Pomodoro timer that provides a personalized user experience according to individual preferences.

## ✨ 機能 / Features

### ⏰ 時間設定の柔軟化 / Flexible Time Settings
- **作業時間**: 15分 / 25分 / 35分 / 45分から選択
- **休憩時間**: 5分 / 10分 / 15分から選択
- **Work Duration**: Choose from 15/25/35/45 minutes
- **Break Duration**: Choose from 5/10/15 minutes

### 🎨 テーマ切り替え / Theme Switching
- **ライトモード**: 明るい表示 📝
- **ダークモード**: 暗い表示 🌙  
- **フォーカスモード**: 集中用 🎯
- **Light Mode**: Bright display
- **Dark Mode**: Dark display
- **Focus Mode**: For concentration

### 🔊 サウンド設定 / Sound Settings
- **開始音**: タイマー開始時の音
- **終了音**: タイマー終了時の音
- **tick音**: 毎秒のチック音
- **Start Sound**: Sound when timer starts
- **End Sound**: Sound when timer ends
- **Tick Sound**: Sound every second

### 💾 設定の永続化 / Settings Persistence
- 設定は自動的に保存され、次回起動時に復元されます
- Settings are automatically saved and restored on next startup

## 🚀 使用方法 / Usage

### 基本的な使用 / Basic Usage

```bash
# メインアプリケーションを起動
python3 main.py

# デモを実行
python3 demo.py

# テストを実行
python3 test_pomodoro.py
```

### プログラムからの使用 / Programmatic Usage

```python
from pomodoro_timer import PomodoroTimer, PomodoroSettings, WorkDuration, BreakDuration, Theme
from settings_manager import SettingsManager

# カスタム設定でタイマーを作成
settings = PomodoroSettings(
    work_duration=WorkDuration.EXTENDED,  # 45分
    break_duration=BreakDuration.LONG,    # 15分
    theme=Theme.FOCUS                     # フォーカスモード
)

timer = PomodoroTimer(settings)
timer.start()
```

## 📁 ファイル構成 / File Structure

```
├── main.py              # メインアプリケーション / Main application
├── pomodoro_timer.py    # タイマー実装 / Timer implementation
├── settings_manager.py  # 設定管理 / Settings management
├── test_pomodoro.py     # テストスイート / Test suite
├── demo.py              # デモスクリプト / Demo script
├── deliverManager.py    # 既存のコード / Existing code
└── README.md            # このファイル / This file
```

## 🧪 テスト / Testing

包括的なテストスイートが含まれています:

```bash
python3 test_pomodoro.py
```

テストカバレッジ:
- ✅ 基本的なタイマー機能
- ✅ 設定のカスタマイズ
- ✅ 設定の永続化
- ✅ イベントハンドリング
- ✅ エラーハンドリング

## 📋 設定例 / Configuration Examples

### デフォルト設定 / Default Settings
- 作業時間: 25分
- 休憩時間: 5分
- テーマ: ライト
- サウンド: 開始音・終了音有効、tick音無効

### カスタム設定例 / Custom Configuration Example
```json
{
  "work_duration": 45,
  "break_duration": 15,
  "theme": "focus",
  "sound_settings": {
    "start_sound": true,
    "end_sound": true,
    "tick_sound": false
  }
}
```

## 🎯 テスト目的 / Testing Purpose

個人の好みに合わせた設定がユーザー継続率に与える影響を測定する。

Measure the impact of personalized settings on user retention rates.

## 💻 システム要件 / System Requirements

- Python 3.6+
- 標準ライブラリのみ使用 (外部依存なし)
- Uses only standard library (no external dependencies)

## 🔧 開発者向け情報 / Developer Information

### アーキテクチャ / Architecture
- オブジェクト指向設計
- イベント駆動アーキテクチャ
- 設定とロジックの分離
- スレッドセーフなタイマー実装

### 拡張性 / Extensibility
新しい機能は以下の方法で簡単に追加できます:
- 新しい時間設定のEnumへの追加
- 新しいテーマの追加
- 追加のサウンド設定
- カスタムイベントハンドラー
