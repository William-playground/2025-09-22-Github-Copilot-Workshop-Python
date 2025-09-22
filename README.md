# ポモドーロタイマー - 視覚的フィードバック強化版

Enhanced Pomodoro Timer with Visual Feedback

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![GUI](https://img.shields.io/badge/GUI-tkinter-green.svg)
![Status](https://img.shields.io/badge/Status-完成-success.svg)

ワークショップの手順：https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0

## 概要

このプロジェクトは、視覚的フィードバックを強化したポモドーロタイマーです。ユーザーの集中力と没入感を向上させるために、動的なアニメーションと色の変化を実装しています。

## 🎨 実装された視覚的機能

### 1. 円形プログレスバーのアニメーション
- 残り時間に応じて滑らかに減少する円弧
- 高精度セグメント描画による美しいアニメーション
- リアルタイム更新（20fps）

### 2. 時間経過による色のグラデーション変化
- **開始時（青色 #4a9eff）**: 集中状態を表現
- **中間時（黄色 #ffb200）**: 注意喚起
- **終了時（赤色 #ff6b6b）**: 緊急状態

### 3. 背景エフェクト
- **パーティクルシステム**: 動的なパーティクルアニメーション
- **波紋エフェクト**: タイマー実行中の同心円波紋
- **アルファブレンド**: 滑らかな透明度変化

## 🚀 使用方法

### 通常版（実用タイマー）
```bash
python3 main.py
```
- 作業時間: 25分
- 休憩時間: 5分

### デモ版（高速テスト用）
```bash
python3 demo_pomodoro.py
```
- 作業時間: 30秒
- 休憩時間: 10秒

### テスト実行
```bash
python3 test_pomodoro.py
```

## 🛠️ 技術仕様

### 環境要件
- Python 3.12+
- tkinter (標準ライブラリ)
- threading (標準ライブラリ)

### アーキテクチャ
- **メインクラス**: `PomodoroTimer`
- **パーティクルシステム**: `Particle`クラス
- **マルチスレッド**: タイマー処理の独立実行
- **リアルタイム描画**: 50ms間隔でのUI更新

### 主要メソッド
```python
# 色計算アルゴリズム
def get_progress_color(self, progress: float) -> str:
    """青→黄→赤のグラデーション計算"""

# パーティクル生成
def spawn_particles(self):
    """動的パーティクルエフェクト生成"""

# 波紋エフェクト
def draw_ripple_effect(self):
    """同心円波紋アニメーション"""

# プログレスバー描画
def draw_progress_circle(self):
    """滑らかな円弧プログレスバー"""
```

## 📊 テスト結果

全10個のユニットテストが合格：

```bash
=== ユニットテスト実行 ===
test_particle_creation ... ok
test_particle_death ... ok  
test_particle_update ... ok
test_particle_system_integration ... ok
test_blend_alpha ... ok
test_initial_state ... ok
test_progress_color_calculation ... ok
test_session_switching ... ok
test_time_formatting ... ok
test_timer_reset ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.025s

OK
```

## 🎮 操作方法

### ボタン
- **開始/停止**: タイマーの開始と一時停止
- **リセット**: タイマーを初期状態に戻す

### 自動機能
- 作業セッション終了後、自動的に休憩時間に切り替え
- 休憩時間終了後、自動的に作業セッションに戻る
- セッション表示の色変更（作業: 青、休憩: 緑）

## 🔧 カスタマイズ

### タイマー時間の変更
```python
# main.pyの設定
self.work_duration = 25 * 60  # 25分（秒単位）
self.break_duration = 5 * 60  # 5分（秒単位）
```

### 色の調整
```python
# 色グラデーションのカスタマイズ
def get_progress_color(self, progress: float) -> str:
    # 開始色、中間色、終了色を変更可能
```

### パーティクル設定
```python
# パーティクル生成数の調整
if len(self.particles) < 50:  # 最大数を変更
    for _ in range(2):  # 生成数を変更
```

## 📁 ファイル構成

```
.
├── main.py              # メインアプリケーション
├── demo_pomodoro.py     # デモ版（高速テスト用）
├── test_pomodoro.py     # テストスイート
├── deliverManager.py    # 既存のコード（未使用）
├── pomodoro.png         # アイコン画像
├── .gitignore          # Git設定
└── README.md           # このファイル
```

## 🎯 設計コンセプト

### 視覚的没入感
- ダークテーマによる目の疲労軽減
- 動的エフェクトによる集中力向上
- 色の心理効果を活用した進行状況表示

### ユーザビリティ
- 直感的なインターフェース
- リアルタイムフィードバック
- 最小限の操作で最大の効果

### パフォーマンス
- 軽量な実装（標準ライブラリのみ）
- 効率的なアニメーションアルゴリズム
- メモリ使用量の最適化

## 🚦 今後の拡張可能性

- [ ] 音響エフェクトの追加
- [ ] タスク管理機能の統合
- [ ] 統計データの保存
- [ ] カスタムテーマの対応
- [ ] 通知機能の実装

## 🤝 コントリビューション

このプロジェクトは GitHub Copilot Workshop の一環として開発されました。改善提案やバグ報告は Issue でお知らせください。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**開発者**: GitHub Copilot & Human Collaboration  
**最終更新**: 2024年9月22日
