# WSL 本地可视化需求与解决方案报告

## 1. 需求定义
- 用户目标：在 **WSL 环境** 中运行 VULCA prototype，并在本机浏览器直接可视化操作（非仅命令行）。
- 期望入口：可访问的本地 Web UI（优先 `localhost`，备选 WSL IP）。
- 业务诉求：可手动输入任务、看到候选与评分输出、可重复验证。

## 2. 已执行解决方案
- 安装可视化依赖：
  - `cd <project-root>/wenxin-backend`
  - `venv/bin/pip install gradio>=5.0.0`
- 启动 Gradio 原型界面（WSL 绑定）：
  - `GRADIO_SERVER_NAME=0.0.0.0 GRADIO_SERVER_PORT=7860 venv/bin/python -m app.prototype.ui.gradio_demo`
- 连通性探测（在当前执行环境内）：
  - `curl http://127.0.0.1:7860/` -> `200`
  - `curl http://172.19.52.44:7860/` -> `200`（示例 WSL IP）

## 3. 当前结论
- Prototype UI 已可在 WSL 侧启动，且端口监听验证通过。
- 但用户侧浏览器仍报告“不可访问”，说明问题已从“服务未启动”转为“主机到 WSL 访问链路”问题。

## 4. 建议的下一步（按优先级）
1. 在 Windows PowerShell 直接验证：
   - `curl http://localhost:7860`
   - `curl http://<WSL_IP>:7860`
2. 若失败，检查 WSL 端口转发与防火墙策略。
3. 若仅临时会话可用，改为长期运行方式（tmux/systemd user service）保证服务不掉线。
4. 完成后再接入前端主站路由，避免把网络层问题误判为业务代码问题。

