# ポモドーロタイマー Web アプリケーション アーキテクチャ

## 1. 目的 / スコープ
- 直感的でシンプルなポモドーロタイマー（25分集中 + 休憩）をブラウザで提供。
- 今日の完了回数 / 集中時間を即時フィードバック。
- 将来的な拡張（ユーザ管理、統計分析、通知、同期、PWA / モバイル対応）を見据えた疎結合な構成。

## 2. 設計方針（キーポイント）
| 観点 | 方針 |
|------|------|
| タイマー精度 | クライアントで高頻度計測（ミリ秒換算）、サーバは整合性チェック（開始時刻 + 予定秒）。|
| 状態管理 | クライアントとサーバで同一の状態概念（モード / 残り時間 / フェーズ）。最終確定はサーバ。|
| 通信 | 初期は REST + ポーリング。将来 WebSocket / SSE にスイッチ可能な抽象レイヤ。|
| 拡張性 | Flask Blueprints + ドメインサービス + Repository 抽象。|
| テスト容易性 | 時刻依存を `time_provider` で抽象化。状態遷移を純粋ロジック化。|
| パフォーマンス | リアルタイム計測はクライアント側、サーバは少量のイベント処理と集計。|

## 3. レイヤ構成
```
Presentation（Blueprint/API, HTML, JS）
 ├─ Application / Domain Services（timer_service, stats_service）
 │   ├─ Domain Models（PomodoroSession, Enums）
 │   └─ Repositories（DB抽象）
 └─ Infrastructure（SQLAlchemy, time_provider, event_bus など）
```
- 双方向イベント伝搬部は後で WebSocket 実装を追加可能なように `presentation` 層で分離。

## 4. 推奨ディレクトリ構造
```
project_root/
  app/
    __init__.py            # create_app()
    config.py              # 設定クラス（Dev/Prod/Test）
    extensions.py          # db, migrate, socket, cache 等
    blueprints/
      ui/                  # SSR (任意)
        routes.py
      api/
        routes_timer.py    # /api/timer/*
        routes_stats.py    # /api/stats/*
      health/
        routes.py
    domain/
      models.py
      value_objects.py     # Enum / 小さなVO
      services/
        timer_service.py
        stats_service.py
        session_service.py # 将来ユーザ対応
    infrastructure/
      repositories/
        pomodoro_repo.py
      time_provider.py
      event_bus.py
    presentation/
      serializers.py
      validators.py
    tasks/                 # 非同期(Celery等導入時)
  front/
    assets/
      css/
        base.css
        components/
          circular-progress.css
      js/
        core/
          apiClient.js
          eventBus.js
          stateStore.js
          timer.js
          websocket.js      # 導入時
        ui/
          progressRing.js
          controls.js
          statsPanel.js
        main.js
    index.html
  migrations/
  tests/
    unit/
    integration/
    e2e/
  static/                 # ビルド成果物
  templates/              # Jinja2 (必要なら)
  requirements.txt or pyproject.toml
  wsgi.py
```

## 5. ドメインモデル（初期）
- `PomodoroSession`:
  - id, user_id(将来), mode(FOCUS/SHORT_BREAK/LONG_BREAK), start_at, end_at,
    planned_length_sec, actual_length_sec, status(COMPLETED/INTERRUPTED)
- `TimerState`（メモリ or キャッシュ保持用）:
  - mode, phase_start_at, planned_duration_sec, remaining_sec（計算可）、state(IDLE/RUNNING/PAUSED)
- Enums: `TimerMode`, `TimerLifecycleState`, `SessionStatus`。

## 6. タイマー責務分担
| 項目 | クライアント | サーバ |
|------|--------------|--------|
| 時間カウント | 高精度・表示 | 公式基準 (start_at + planned) 計算のみ |
| 状態遷移トリガ | 発火 | 検証 / 永続化 |
| 統計更新 | - | セッション終了時記録 |
| 復元 | 初期ロード要求 | 現在状態返却 |
| 多タブ調停 | 表示 | 排他検証（同時二重開始拒否） |

## 7. 状態マシン
States:
`IDLE, FOCUS_RUNNING, FOCUS_PAUSED, BREAK_RUNNING, BREAK_PAUSED, COMPLETED, ABORTED`

主遷移例:
- IDLE -> FOCUS_RUNNING (startFocus)
- FOCUS_RUNNING -> FOCUS_PAUSED (pause)
- FOCUS_PAUSED -> FOCUS_RUNNING (resume)
- FOCUS_RUNNING -> BREAK_RUNNING (autoComplete)
- BREAK_RUNNING -> IDLE (breakFinished) / ループ（LONG_BREAK インターバル後）
- 任意 -> ABORTED (reset)

サーバ側 `timer_service` でテーブル化し遷移検証（不正遷移は 409 / 422）。

## 8. API 設計（MVP）
| メソッド | パス | 目的 | 入力例 | 出力例 |
|----------|------|------|--------|--------|
| POST | /api/timer/start | 集中開始 | {mode:"focus", lengthSec?:1500} | {state,...} |
| POST | /api/timer/pause | 一時停止 | - | {state:"focus_paused"} |
| POST | /api/timer/resume | 再開 | - | {state:"focus_running"} |
| POST | /api/timer/reset | 中断/初期化 | - | {state:"idle"} |
| GET  | /api/timer/state | 現在状態 | - | {mode, state, remainingSec,...} |
| GET  | /api/stats/today | 今日統計 | - | {completedCount, focusTotalSec, sessions:[...]} |
| GET  | /api/stats/week | 週次統計 | - | {daily:[...]} |

リアルタイム化: `/api/stream/timer` (SSE) もしくは `/ws` (WebSocket)。

## 9. フロントエンド構成
- `apiClient.js`: fetch ラッパ・共通エラー処理。
- `eventBus.js`: 低コスト Pub/Sub（subscribe, emit）。
- `stateStore.js`: 単一状態オブジェクト（timerState, stats）。
- `timer.js`: クライアント計測。`start()` で `startTimestamp` 記録し `elapsed = now - start` から残り計算（ドリフト補正）。
- `progressRing.js`: SVG (円周 = 2πR)。stroke-dasharray / stroke-dashoffset で進捗表示。
- `controls.js`: UI操作 -> eventBus -> api 呼び出し。
- `statsPanel.js`: 今日統計描画・更新。
- `websocket.js`: 後付リアルタイムイベント -> stateStore 反映。

更新フロー（開始ボタン）:
1. ユーザ操作 -> emit('REQUEST_START').
2. ハンドラが `apiClient.post('/api/timer/start')`。
3. レスポンスを `stateStore.commit()`。
4. commit で `eventBus.emit('STATE_CHANGED')`。
5. UI各部が再描画。

## 10. 進捗リング仕様
- `circumference = 2 * Math.PI * radius`。
- `progressRatio = elapsed / planned`。
- `strokeDashoffset = circumference * (1 - progressRatio)`。
- 250ms 間隔の計算 + `requestAnimationFrame` で描画最適化。SVGで十分。パフォーマンスが問題化したら Canvas 切替検討。

## 11. 統計計算
- セッション終了イベント（FOCUS完了）で DB に `PomodoroSession` 永続化。
- 今日統計: `SELECT count(*), SUM(actual_length_sec) WHERE date(start_at)=today AND status='COMPLETED' AND mode='focus'`。
- 将来: キャッシュ（Redis / in-memory）と無効化戦略。MVP は直接クエリ。

## 12. 設定 / カスタマイズ
`config.py`:
```
FOCUS_DEFAULT_SEC = 25*60
SHORT_BREAK_SEC = 5*60
LONG_BREAK_SEC = 15*60
LONG_BREAK_INTERVAL = 4  # 何回毎にロング休憩
```
ユーザごとの設定拡張時は `user_settings` テーブル。（バリデーション: 最小/最大範囲）

## 13. セキュリティ / 信頼性
- CSRF対策（Cookieセッション運用時）。
- 不正遷移（例: PAUSED 以外で resume）は 409/422 を返却。
- 二重開始防止: 既存 RUNNING セッション存在時に start 拒否。
- 入力検証: `lengthSec` 範囲チェック (例: 5〜120分)。
- ログ出力: state change ごとに構造化 JSON。

## 14. テスト戦略
| レベル | 対象 | 手法 |
|--------|------|------|
| Unit | timer_service 状態遷移 | パラメタライズで全遷移網羅 |
| Unit | stats_service 集計 | モックデータ / in-memory DB |
| Integration | API エンドポイント | Flask test client + sqlite memory |
| E2E | 主要フロー(開始→完了→統計更新) | Playwright / drift短縮のため time_provider モック |

## 15. ログ / オブザーバビリティ
- ログ: `session_started`, `session_completed`, `session_aborted`。
- 構造: `{event, user_id, mode, planned_sec, actual_sec, ts}`。
- 将来: OpenTelemetry / APM 導入余地。

## 16. パフォーマンス & スケール
- 初期: 単一 gunicorn worker + SQLite で十分。
- トラフィック増: PostgreSQL + 監視。WebSocket 需要が高まれば ASGI (uvicorn + FastAPI への移行も容易なレイヤ分離)。
- サーバは高頻度 tick を送らず、状態変化イベント中心 → 接続数増でも低負荷。

## 17. 開発ロードマップ（フェーズ）
1. プロジェクト骨組み（create_app, Blueprints, DB初期化）
2. Timer REST API + フロント最小UI（残り時間・開始/リセット）
3. セッション記録 & 今日統計表示
4. 状態マシン単体テスト & API統合テスト
5. ポーリング → SSE/WebSocket 切替
6. ロングブレーク / インターバル設定 & UI反映
7. 通知(PWA) / Service Worker
8. ユーザ認証 & 個別統計
9. 週間 / 月間分析ビュー
10. パフォーマンス改善 / モバイル最適化

## 18. リスクと対策
| リスク | 説明 | 対策 |
|--------|------|------|
| タイマーずれ | タブスリープ / setInterval 遅延 | 経過 = now - startAt 計算で補正、サーバ検証 |
| 多タブ競合 | 複数開始要求 | サーバ側排他 + クライアント警告 |
| 将来の技術移行 | Flask→ASGI | ドメイン層をフレームワーク非依存に維持 |
| 不正API呼出 | 手製JS改変 | 状態遷移検証 + 監査ログ |
| 遅延統計反映 | 完了イベント漏れ | セッション終了時にトランザクション確実化 |

## 19. 将来拡張アイデア
- ユーザ毎の習慣スコアリング / ヒートマップ。
- AI 提案（集中時間帯レコメンド）。
- Slack / Discord Webhook 連携。
- マルチデバイスリアルタイム同期（WebSocket）。
- オフライン蓄積 → 再接続差分同期 (/api/sync)。
- 国際化（i18n）とアクセシビリティ (a11y) 強化。

## 20. MVP 成功条件
- 25分開始～完了→自動で休憩遷移 or IDLE戻り。
- 今日の完了数 / 集中総時間が即更新。
- リロード時に進行中タイマーが復元される（残り時間再計算）。
- 基本的な単体・統合テストが緑。

---
このドキュメントは初期実装前の指針です。実装進行に伴い、実測値・運用課題を反映して随時改訂してください。
