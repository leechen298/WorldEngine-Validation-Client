# ADR 0001：第一版技术栈

状态：接受
日期：2026-06-02

## 决策

第一版采用：

- React + Vite + TypeScript 作为 Web 前端。
- PixiJS 作为像素世界画面基础。
- Zustand 作为轻量前端状态管理。
- Python + FastAPI + Pydantic 作为本地验证客户端后端。
- SQLite 作为本地数据库。

## 背景

验证客户端需要：

- Web 调试便利性。
- 会话库和运行控制台。
- 本地日志、snapshot、diff 和 branch 存储。
- 与 WorldEngine 公开 API 通信。
- 保持未来向游戏客户端演进的可能。

用户更熟悉有后端和数据库的模型，不希望第一版主要依赖 IndexedDB。

## 理由

React 生态成熟，适合快速构建复杂 Web UI。

PixiJS 适合 Web 像素画面和后续轻量动画，不需要第一版直接引入更重的游戏引
擎。

FastAPI 与 WorldEngine 技术方向接近，Pydantic 适合处理结构化 API payload。

SQLite 足够支持本地 session、commit point、branch、event、diff、snapshot
和 evidence metadata。

## 后果

第一版需要同时启动 Web 前端和 FastAPI 后端。

如果未来发布为桌面游戏客户端，可以继续沿用 SQLite，并考虑 Tauri/Electron
或其他客户端壳。

如果未来需要云端同步或多人运行，可以在后续版本评估 Postgres。
