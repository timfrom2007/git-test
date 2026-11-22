# AI 賺錢主控台

主控 agent 負責發想、派工、驗收；子 agent（獨立的 cloud session）負責執行；人類每天花約 1 小時做只有人能做的事。

## 目錄
- `control/RULES.md`：所有 agent 必須遵守的規則
- `control/sessions.md`：子 session 清單（ID、負責 project、分支）
- `control/tasks.md`：任務板
- `control/human-todo.md`：需要人類處理的事項（每天 1 小時內）
- `control/ideas.md`：點子池與評分
- `reports/YYYY-MM-DD.md`：每日主控回報
- `projects/<name>/`：各 project 的規格、進度、成果

## 主分支
所有主控狀態以 `claude/gifted-ride-nnfsux` 分支上的檔案為準。
