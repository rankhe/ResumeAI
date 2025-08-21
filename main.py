"""
简历助手主应用文件
提供一键生成匹配简历、智能匹配、ATS优化等功能
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import json
from datetime import datetime

app = FastAPI(
    title="简历助手",
    description="一款智能简历优化工具，可根据目标职位自动优化简历内容，提高通过ATS筛选系统的概率",
    version="1.0.0"
)

# 添加CORS中间件以允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """根路径，返回前端主页面"""
    # 默认重定向到用户信息维护页面，让前端JavaScript处理用户状态检查
    if os.path.exists("frontend/user-profile.html"):
        with open("frontend/user-profile.html", "r", encoding="utf-8") as f:
            return f.read()
    else:
        return """
        <html>
            <head>
                <title>简历助手</title>
            </head>
            <body>
                <h1>简历助手</h1>
                <p>欢迎使用简历助手API</p>
                <p>前端文件未找到，请检查 frontend/user-profile.html 文件是否存在</p>
                <a href="/docs">查看API文档</a>
            </body>
        </html>
        """

# 尝试导入用户交互模块，如果失败则使用内置的简化版本
try:
    from user_interface import UserInterface
    ui = UserInterface()
    MODULES_AVAILABLE = True
    print("✅ 用户交互模块加载成功")
except ImportError as e:
    print(f"❌ 无法导入用户交互模块: {e}")
    ui = None
    MODULES_AVAILABLE = False
except Exception as e:
    print(f"❌ 用户交互模块初始化失败: {e}")
    ui = None
    MODULES_AVAILABLE = False

# 如果模块加载失败，使用简化的内置版本
class SimpleUserInterface:
    """简化的用户交互接口，用于演示"""
    
    def generate_resume_by_description(self, description, resume_path, file_type='pdf'):
        return {
            "success": True,
            "message": "简历生成成功（演示模式）",
            "match_score": 0.85,
            "suggestions": [
                "增加Python相关项目经验",
                "突出FastAPI开发经验", 
                "添加机器学习相关技能"
            ],
            "ats_suggestions": [
                "优化关键词密度",
                "调整简历结构以适应ATS系统",
                "添加标准技能术语"
            ],
            "generated_file": "demo_resume.pdf"
        }
    
    def generate_resume_by_url(self, url, resume_path, file_type='pdf'):
        return {
            "success": True,
            "message": "简历生成成功（演示模式）",
            "match_score": 0.88,
            "suggestions": [
                "增加Web开发相关经验",
                "突出RESTful API设计能力",
                "添加Docker部署经验"
            ],
            "ats_suggestions": [
                "确保使用标准职位关键词",
                "优化简历格式以适应ATS解析",
                "强调量化的工作成果"
            ],
            "generated_file": "demo_resume.pdf"
        }
    
    def generate_resume_by_template(self, template_name, resume_path, file_type='pdf'):
        return {
            "success": True,
            "message": "简历生成成功（演示模式）",
            "match_score": 0.90,
            "suggestions": [
                "增加项目管理经验",
                "突出团队协作能力",
                "添加敏捷开发经验"
            ],
            "ats_suggestions": [
                "确保简历结构清晰",
                "使用标准的简历部分标题",
                "优化关键词匹配度"
            ],
            "generated_file": "demo_resume.pdf"
        }

if not MODULES_AVAILABLE:
    ui = SimpleUserInterface()

def check_modules_available():
    """
    检查模块是否可用，如果不可用则抛出异常
    """
    if not MODULES_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="服务暂时不可用：核心模块未正确加载，请检查依赖项安装"
        )

class JobDescriptionRequest(BaseModel):
    description: str

class JobUrlRequest(BaseModel):
    url: str

class TemplateRequest(BaseModel):
    template_name: str

class ResumeOptimizationResponse(BaseModel):
    match_score: float
    suggestions: List[str]
    ats_suggestions: List[str]
    generated_file: str

@app.get("/api")
async def api_info():
    """API信息接口"""
    return {
        "message": "欢迎使用简历助手API", 
        "version": "1.0.0",
        "description": "智能简历优化工具，帮助您的简历更好地匹配目标职位",
        "modules_available": MODULES_AVAILABLE
    }

@app.post("/generate-by-description")
async def generate_by_description(
    description: str = Form(...), 
    resume: UploadFile = File(None),
    user_id: str = Form(None)
):
    """
    根据职位描述生成简历
    """
    check_modules_available()
    
    try:
        resume_path = None
        file_type = 'pdf'
        
        # 如果有上传简历文件，则保存
        if resume and resume.filename:
            resume_path = f"uploaded_resume_{int(datetime.now().timestamp())}_{resume.filename}"
            with open(resume_path, "wb") as buffer:
                buffer.write(await resume.read())
            file_type = resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        
        # 生成简历
        result = ui.generate_resume_by_description(
            description, 
            resume_path, 
            file_type,
            user_id
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        # 清理上传的文件
        if resume_path and os.path.exists(resume_path):
            os.remove(resume_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/generate-by-url")
async def generate_by_url(
    url: str = Form(...), 
    resume: UploadFile = File(None),
    user_id: str = Form(None)
):
    """
    根据职位链接生成简历
    """
    check_modules_available()
    
    try:
        resume_path = None
        file_type = 'pdf'
        
        # 如果有上传简历文件，则保存
        if resume and resume.filename:
            resume_path = f"uploaded_resume_{int(datetime.now().timestamp())}_{resume.filename}"
            with open(resume_path, "wb") as buffer:
                buffer.write(await resume.read())
            file_type = resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        
        # 生成简历
        result = ui.generate_resume_by_url(
            url, 
            resume_path, 
            file_type,
            user_id
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        # 清理上传的文件
        if resume_path and os.path.exists(resume_path):
            os.remove(resume_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/generate-by-template")
async def generate_by_template(
    template_name: str = Form(...), 
    resume: UploadFile = File(None),
    user_id: str = Form(None)
):
    """
    根据模板生成简历
    """
    check_modules_available()
    
    try:
        resume_path = None
        file_type = 'pdf'
        
        # 如果有上传简历文件，则保存
        if resume and resume.filename:
            resume_path = f"uploaded_resume_{int(datetime.now().timestamp())}_{resume.filename}"
            with open(resume_path, "wb") as buffer:
                buffer.write(await resume.read())
            file_type = resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        
        # 生成简历
        result = ui.generate_resume_by_template(
            template_name, 
            resume_path, 
            file_type,
            user_id
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        # 清理上传的文件
        if resume_path and os.path.exists(resume_path):
            os.remove(resume_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/upload-resume")
async def upload_resume(resume: UploadFile = File(...)):
    """
    上传简历文件
    """
    check_modules_available()
    
    try:
        # 生成唯一的文件名
        import uuid
        file_extension = resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        unique_filename = f"uploaded_resume_{uuid.uuid4().hex}.{file_extension}"
        
        # 保存文件
        with open(unique_filename, "wb") as buffer:
            buffer.write(await resume.read())
        
        # 保存文件信息到会话（简化处理，实际应用中应使用数据库）
        return {
            "success": True,
            "message": "简历上传成功",
            "filename": unique_filename,
            "original_name": resume.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/templates")
async def get_templates():
    """获取可用模板列表"""
    try:
        templates_dir = "templates"
        if os.path.exists(templates_dir):
            template_files = [f.replace('.json', '') for f in os.listdir(templates_dir) if f.endswith('.json')]
            return {"templates": template_files}
        else:
            return {"templates": ["software_engineer", "data_analyst"]}
    except Exception as e:
        return {"templates": ["software_engineer", "data_analyst"]}

@app.get("/history")
async def get_history():
    """获取生成历史记录"""
    try:
        history_file = "generation_history.json"
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            # 如果文件直接存储数组，则直接返回；如果是对象，则提取history字段
            if isinstance(history_data, list):
                return {"history": history_data}
            else:
                return {"history": history_data.get("history", [])}
        else:
            # 返回空历史记录
            return {"history": []}
    except Exception as e:
        print(f"读取历史记录失败: {e}")
        return {"history": []}

@app.get("/download/{filename}")
async def download_file(filename: str):
    """下载生成的简历文件"""
    # 安全检查，防止路径遍历攻击
    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="无效的文件名")
    
    # 对于演示文件，返回一个简单的响应
    if filename.startswith("demo_"):
        raise HTTPException(status_code=404, detail="演示文件不可下载，请生成真实简历")
    
    # 首先尝试原始文件名
    file_path = filename
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # 如果原始文件名不存在，尝试带重复扩展名的文件名（处理历史遗留问题）
    if filename.endswith('.pdf'):
        duplicate_ext_path = filename + '.pdf'
    elif filename.endswith('.docx'):
        duplicate_ext_path = filename + '.docx'
    else:
        duplicate_ext_path = None
    
    if duplicate_ext_path and os.path.exists(duplicate_ext_path):
        return FileResponse(duplicate_ext_path)
    
    raise HTTPException(status_code=404, detail="文件未找到")

def check_modules_available():
    """检查模块是否可用"""
    if not MODULES_AVAILABLE:
        raise HTTPException(status_code=503, detail="核心模块未加载，请检查依赖项安装")

# 导入模型类
from models import (
    UserProfile, 
    ResumeContent, 
    WorkExperience, 
    Education, 
    Skill, 
    Certificate, 
    Project, 
    Language,
    ResumeFile, 
    ResumeFormats, 
    UserResumeManager
)

# 初始化用户简历管理器
user_manager = UserResumeManager()

@app.post("/users")
async def create_user(profile: UserProfile):
    """
    创建用户
    """
    try:
        user = user_manager.create_user(profile)
        return {
            "success": True,
            "message": "用户创建成功",
            "user": user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建用户失败: {str(e)}")

@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """
    获取用户信息
    """
    try:
        print(f"正在获取用户信息: {user_id}")
        user = user_manager.get_user(user_id)
        if user:
            print(f"用户信息获取成功: {user_id}")
            return {
                "success": True,
                "profile": user
            }
        else:
            print(f"用户不存在: {user_id}")
            raise HTTPException(status_code=404, detail="用户不存在")
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"获取用户信息时发生异常: {user_id}, 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取用户信息失败: {str(e)}")

@app.put("/users/{user_id}")
async def update_user(user_id: str, profile: UserProfile):
    """
    更新用户信息
    """
    try:
        profile.user_id = user_id
        user = user_manager.update_user(profile)
        return {
            "success": True,
            "message": "用户信息更新成功",
            "user": user
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新用户信息失败: {str(e)}")

if __name__ == "__main__":
    print("=== 简历助手服务器启动 ===")
    print()
    
    # 检查前端文件
    print("📁 前端文件检查:")
    frontend_files = [
        "frontend/index.html",
        "frontend/src/script.js", 
        "frontend/src/style.css"
    ]
    
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
    
    print()
    print("🔧 模块状态:")
    if MODULES_AVAILABLE:
        print("✅ 所有核心模块已加载")
    else:
        print("⚠️  核心模块未完全加载，将使用演示模式")
    
    print()
    print("🚀 启动服务器...")
    print("🌐 访问地址: http://localhost:8000")
    print("🛑 按 Ctrl+C 停止服务器")
    print()
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
