# Task Management CLI Tool

MySQLを使用したタスク管理ツールです。

## データベースの初期化

以下のSQLをコピーして実行してください。
```SQL
CREATE DATABASE IF NOT EXISTS task_management;
USE task_management;

DROP TABLE IF EXISTS tasks;
CREATE TABLE tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    description TEXT,
    assignee    VARCHAR(100),
    deadline    DATE,
    status      VARCHAR(50),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at  DATETIME DEFAULT NULL
);
```

## セットアップと実行

1. 依存ライブラリのインストール
```bash
pip install mysql-connector-python
```
2. 各機能の実行

| 操作 | CRUD | 実行コマンド |
| :---: | :--- | :--- |
| 追加 | Create | `python task_app.py add` |
| 一覧 | Read | `python task_app.py list` |
| 更新 | Update | `python task_app.py update` |
| 削除 | Delete | `python task_app.py delete` |