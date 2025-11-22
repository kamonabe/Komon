# Requirements Document

## Introduction

この機能は、Komonが検知したシステムメトリクスの異常や警告をローカルファイルに記録し、後から確認できるようにする通知履歴機能です。Slack等の外部通知サービスが使えない環境でも、Komonの検知情報を見逃さずに確認できることを目的としています。

## Glossary

- **Notification System**: Komonのシステムメトリクス監視結果を通知する機能
- **Notification History**: 過去に発生した通知の記録
- **Queue File**: 通知履歴を保存するJSONファイル（`notifications/queue.json`）
- **Advise Command**: Komonの助言表示コマンド（`komon advise`）
- **Metric Type**: 監視対象の種類（CPU使用率、メモリ使用率、ディスク使用率等）

## Requirements

### Requirement 1

**User Story:** システム管理者として、Komonが検知した通知を後から確認したいので、通知履歴がローカルに保存される機能が必要です。

#### Acceptance Criteria

1. WHEN the Notification System sends a notification THEN the Notification System SHALL save the notification data to the Queue File
2. WHEN saving notification data THEN the Notification System SHALL include timestamp, metric type, metric value, and message text
3. WHEN the Queue File does not exist THEN the Notification System SHALL create the Queue File and its parent directory
4. WHEN the Queue File contains 100 or more notifications THEN the Notification System SHALL remove the oldest notification before adding a new one
5. WHEN saving fails due to file system errors THEN the Notification System SHALL log the error and continue normal operation without crashing

### Requirement 2

**User Story:** システム管理者として、保存された通知履歴を簡単に確認したいので、既存のコマンドで履歴を表示できる機能が必要です。

#### Acceptance Criteria

1. WHEN a user executes the Advise Command without options THEN the Advise Command SHALL display all notifications from the Notification History
2. WHEN a user executes the Advise Command with `--history N` option THEN the Advise Command SHALL display the most recent N notifications
3. WHEN displaying notifications THEN the Advise Command SHALL show timestamp, metric type, metric value, and message in a readable format
4. WHEN the Queue File does not exist THEN the Advise Command SHALL display a message indicating no history is available
5. WHEN the Queue File is corrupted or invalid JSON THEN the Advise Command SHALL display an error message and continue without crashing

### Requirement 3

**User Story:** システム管理者として、通知履歴が無制限に増えてディスクを圧迫しないように、履歴の保存件数に上限が設定されている必要があります。

#### Acceptance Criteria

1. WHEN the Notification History reaches 100 notifications THEN the Notification System SHALL maintain exactly 100 notifications by removing the oldest
2. WHEN removing old notifications THEN the Notification System SHALL preserve the chronological order of remaining notifications
3. WHEN the Queue File is read THEN the Notification System SHALL validate the data structure and handle invalid entries gracefully

### Requirement 4

**User Story:** 開発者として、既存のKomon機能に影響を与えずに通知履歴機能を追加したいので、既存コードとの統合が適切に行われる必要があります。

#### Acceptance Criteria

1. WHEN the notification history feature is enabled THEN the existing notification functionality SHALL continue to work without modification
2. WHEN notification saving fails THEN the Notification System SHALL still send notifications through configured channels (Slack, etc.)
3. WHEN the Advise Command displays history THEN the existing advise functionality SHALL remain accessible
4. WHEN running existing tests THEN all tests SHALL pass without modification
