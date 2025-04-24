# FlowA

FlowA是一个基于节点的可视化工作流编排引擎，允许用户通过连接不同功能的节点来创建和执行复杂的工作流。它采用前后端分离架构，提供了丰富的内置节点类型和可扩展的插件系统。

## 项目特点

- **可视化工作流设计**：通过直观的拖拽界面创建和编辑工作流
- **节点化编程**：使用各种功能节点构建复杂逻辑，无需编写大量代码
- **增量执行**：智能缓存系统，避免重复计算，提高执行效率
- **插件系统**：支持自定义节点和功能扩展
- **实时反馈**：使用SSE（Server-Sent Events）提供实时执行状态和结果
- **版本管理**：支持工作流的版本控制和历史记录

## 系统架构

FlowA采用前后端分离的架构：

### 前端 (Frontend)

- 基于Vue 3和TypeScript构建
- 使用Naive UI作为UI组件库
- 使用Vue Flow实现节点图编辑器
- 通过HTTP和SSE与后端通信

### 后端 (Backend)

- 基于FastAPI构建的Python后端
- 使用SQLite数据库存储工作流和缓存
- 异步执行引擎，支持并行节点执行
- 插件系统，支持自定义节点类型

## 内置节点类型

FlowA提供了多种内置节点类型，包括：

- **代码解释器**：执行Python代码
- **Jinja2模板**：处理模板渲染
- **LLM推理**：集成大型语言模型，支持OpenAI格式（需要去`plugins/builtin/LLM_inference/FANode_LLM_inference.yaml`填写apikey）
- **迭代运行**：支持（嵌套）循环执行
- **迭代重试**：支持（嵌套）失败重试
- **条件分支**：根据条件执行不同路径
- **分支聚合**：合并多个分支的结果
- **网络请求**：发送HTTP请求

## 安装与运行

### 环境要求

- Python 3.12+
- Node.js 18+
- npm 或 yarn

### 后端安装

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建并激活虚拟环境（可选但推荐）：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 运行后端服务：
   ```bash
   python main.py
   ```

   服务将在 http://localhost:9981 上运行

### 前端安装

1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   # 或
   yarn
   ```

3. 开发模式运行：
   ```bash
   npm run dev
   # 或
   yarn dev
   ```

4. 构建生产版本：
   ```bash
   npm run build
   # 或
   yarn build
   ```

## 使用指南

1. 启动前端和后端服务
2. 在浏览器中访问前端地址（默认为 http://localhost:5173）
3. 创建新工作流或加载现有工作流
4. 右键菜单创建节点
5. 连接节点以创建工作流逻辑
6. 配置节点参数
7. 点击运行按钮执行工作流
8. 通过JINJA2渲染页面查看执行结果和节点输出

## 插件开发

FlowA支持通过插件系统扩展功能。插件开发需要以下文件：

- `config.json`：插件配置文件
- 节点执行代码
- 节点UI配置

详细的插件开发指南请参考 `backend/plugins/README.md`。

## 开发计划

- [x] 异步工作流引擎
- [x] 增加取消机制
- [x] 操作按键组
- [x] 历史记录状态标记
- [x] 选择性节点上传数据
- [x] 响应式结果数据
- [x] LLM节点
- [x] 工作流导入导出
- [x] 复制粘贴
- [x] 解耦节点与引擎
- [x] 多次重试
- [x] 条件分支
- [x] 分支聚合节点
- [x] 网络请求
- [ ] 注释节点
- [ ] API模式

## 贡献指南

欢迎贡献代码、报告问题或提出新功能建议。请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。
