# 简历助手 (Resume Assistant)

一款智能简历优化工具，可根据目标职位自动优化简历内容，提高通过ATS筛选系统的概率。

## 核心价值主张

- **一键生成**：可以根据用户提供的岗位链接，一键生成匹配简历
- **智能匹配**：根据目标职位自动优化简历内容
- **ATS友好**：确保简历能通过自动筛选系统
- **数据驱动**：基于招聘数据提供优化建议
- **多种生成方式**：支持职位描述、职位链接和模板三种方式生成简历
- **标准化模型**：遵循行业标准的简历数据模型设计

## 功能特性

### 1. 职位分析
- 通过职位链接抓取职位描述
- 自动提取关键技能要求
- 分析职位匹配度

### 2. 简历解析
- 支持PDF和DOCX格式简历
- 自动提取联系信息、工作经历、教育背景和技能
- 结构化存储简历数据

### 3. 智能优化
- 计算简历与职位的匹配度
- 提供个性化优化建议
- 自动生成优化后的简历内容

### 4. 简历生成
- 生成ATS友好的PDF格式简历
- 支持多种简历模板
- 导出为PDF、DOCX和HTML格式

### 5. 多种生成方式
- **职位描述生成**：用户描述目标职位，系统自动生成匹配简历
- **职位链接生成**：输入招聘网站链接，一键生成针对该职位的简历
- **模板生成**：选择预设模板，快速生成特定类型简历

### 6. 标准化简历模型
- **必需信息**：用户基本信息、工作经历
- **可选信息**：教育背景、技能证书、项目经历、语言能力等
- **多格式支持**：PDF和DOCX格式提供下载，HTML格式提供在线打印

### 7. 统一简历上传
- 简历只需上传一次，即可用于所有生成方式
- 支持PDF和DOCX格式
- 安全存储和处理

## 技术架构

### 后端技术栈
- **语言**: Python 3.8+
- **框架**: FastAPI
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **异步任务**: Celery + Redis
- **网页抓取**: BeautifulSoup, Requests
- **PDF处理**: ReportLab, python-docx
- **自然语言处理**: NLTK, jieba

### 前端技术栈
- **HTML/CSS/JavaScript**: 原生前端技术
- **响应式设计**: 移动端和桌面端兼容
- **AJAX**: 异步与后端通信

## 项目结构

```
ResumeAI/
├── main.py                 # 应用入口
├── config.py               # 配置文件
├── .env                    # 环境变量
├── requirements.txt        # 依赖包
├── job_analyzer.py         # 职位分析模块
├── resume_parser.py        # 简历解析模块
├── resume_optimizer.py     # 简历优化模块
├── resume_generator.py     # 简历生成模块
├── user_interface.py       # 用户交互模块
├── templates/              # 简历模板目录
│   ├── software_engineer.json
│   └── data_analyst.json
├── uploads/                # 上传文件目录
├── frontend/               # 前端界面目录
│   ├── index.html
│   ├── src/
│   │   ├── style.css
│   │   └── script.js
│   └── README.md
└── README.md              # 项目说明
```

## 安装与运行

### 环境要求
- Python 3.8 或更高版本
- Redis (用于异步任务)

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd ResumeAI
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 安装NLTK数据（首次运行需要）
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. 启动应用
```bash
python main.py
```

应用将在 `http://localhost:8000` 运行，您可以直接访问前端界面。

## API接口

### 根目录
- `GET /` - 应用信息

### 简历生成接口
- `POST /generate-by-description` - 根据职位描述生成简历
- `POST /generate-by-url` - 根据职位链接生成简历
- `POST /generate-by-template` - 根据模板生成简历

### 其他接口
- `GET /templates` - 获取可用模板列表
- `GET /history` - 获取生成历史记录
- `GET /download/{filename}` - 下载生成的简历文件

## 开发计划

### 第一阶段（已完成）
- [x] 基础架构搭建
- [x] 职位分析模块
- [x] 简历解析模块
- [x] 简历优化模块
- [x] 简历生成模块

### 第二阶段（待开发）
- [ ] 用户认证系统
- [ ] 简历存储和管理
- [ ] 前端界面开发
- [ ] 数据库集成
- [ ] 异步任务处理

### 第三阶段（待开发）
- [ ] 移动端应用
- [ ] AI面试模拟
- [ ] 职位推荐系统
- [ ] 简历协作功能

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

[MIT License](LICENSE)