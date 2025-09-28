# ポモドーロタイマー 段階的実装計画

## フェーズ1: プロジェクト骨組み・基盤整備
- Flask プロジェクト初期化（create_app, Blueprint構成）
- SQLite DBセットアップ
- config.py 設定値定義
- タイムプロバイダ抽象（time_provider）
- ヘルスエンドポイント /health 実装
- README（起動手順）

## フェーズ2: タイマー基盤・API実装
- タイマー状態モデル（TimerState）
- 状態マシン実装（IDLE→FOCUS_RUNNING→PAUSE/RESUME→BREAK_RUNNING→IDLE）
- 不正遷移検出（409/422）
- REST API: /api/timer/start, /api/timer/pause, /api/timer/resume, /api/timer/reset, /api/timer/state
- ロギング: state change イベント出力

## フェーズ3: セッション記録・統計API
- PomodoroSession モデル定義
- セッション完了時のDB保存
- 今日統計 API: /api/stats/today

## フェーズ4: フロントエンド MVP
- 単一ページ UI（index.html + CSS）
- タイマー表示（mm:ss カウントダウン / ドリフト補正）
- 開始 / 一時停止 / 再開 / リセット ボタン
- 進捗リング (SVG)
- 今日の完了数 / 集中時間パネル
- 初期ロード時に /api/timer/state, /api/stats/today 取得
- 周期ポーリングで state / stats 更新
- エラーハンドリング

## フェーズ5: テスト・品質向上
- ユニットテスト: 状態遷移
- ユニットテスト: stats 集計
- 統合テスト: start→pause→resume→complete→stats 更新
- 残り時間計算テスト
- エラーレスポンス統一

## フェーズ6: 推奨追加機能（MVP+）
- 長期休憩 / ループ制御（LONG_BREAK_INTERVAL）
- 週次統計 API: /api/stats/week
- SSE / WebSocket 準備
- 多タブ排他
- CI / Lint

## フェーズ7: 中期・将来拡張
- WebSocket (リアルタイム)
- 今日統計キャッシュ
- ロングブレーク設定変更 UI
- 通知機能
- アクセシビリティ
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
各フェーズは、最小限の動作確認・テストを行いながら進めてください。MVP完成後は、ユーザ体験・パフォーマンス・拡張性を意識して段階的に機能追加・改善を行います。