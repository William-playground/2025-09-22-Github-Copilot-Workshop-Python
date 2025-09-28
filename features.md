# ポモドーロタイマー 実装機能一覧

## 1. MVP（必須機能）
### 1-1. タイマー基盤（サーバ）
- タイマー状態モデル（TimerState: mode, phase_start_at, planned_duration_sec, state）
- 状態マシン実装（IDLE→FOCUS_RUNNING→PAUSE/RESUME→BREAK_RUNNING→IDLE）
- 不正遷移検出（409/422）
- API: /api/timer/start, /api/timer/pause, /api/timer/resume, /api/timer/reset, /api/timer/state
- 設定値読込（config.py: FOCUS_DEFAULT_SEC 等）

### 1-2. セッション記録 / 統計（サーバ）
- PomodoroSession モデル定義
- セッション完了時のDB保存
- 今日統計 API: /api/stats/today

### 1-3. フロントエンド（表示 & 操作）
- 単一ページ UI（index.html + CSS）
- タイマー表示（mm:ss カウントダウン / ドリフト補正）
- 開始 / 一時停止 / 再開 / リセット ボタン
- 進捗リング (SVG)
- 今日の完了数 / 集中時間パネル
- 初期ロード時に /api/timer/state, /api/stats/today 取得
- 周期ポーリングで state / stats 更新
- エラーハンドリング

### 1-4. 基盤 / 共通
- Flask create_app() + Blueprint構成
- SQLite DBセットアップ
- タイムプロバイダ抽象（time_provider）
- シリアライザ / バリデーション
- ロギング: state change イベント出力

### 1-5. テスト
- ユニット: 状態遷移
- ユニット: stats 集計
- 統合: start→pause→resume→complete→stats 更新
- 残り時間計算

### 1-6. 非機能
- README（起動手順）
- ヘルスエンドポイント /health
- エラーレスポンス統一

## 2. MVP+（推奨追加機能）
- 長期休憩 / ループ制御（LONG_BREAK_INTERVAL）
- 週次統計 API: /api/stats/week
- SSE / WebSocket 準備
- 多タブ排他
- CI / Lint

## 3. 中期（拡張機能）
- WebSocket (リアルタイム)
- 今日統計キャッシュ
- ロングブレーク設定変更 UI
- 通知機能
- アクセシビリティ

## 4. 将来（ロードマップ）
- ユーザアカウント / 認証
- 個別ユーザ設定 / 同期
- 週間 / 月間 / ヒートマップ可視化
- Slack / Discord Webhook
- PWA (オフライン / push)
- 多デバイスリアルタイム同期
- 高度な統計・AIレコメンド
- OpenTelemetry 導入
- Redis / Celery 非同期
- FastAPI / ASGI 移行

---
この一覧はアーキテクチャ文書に基づき、実装優先度ごとに整理しています。
