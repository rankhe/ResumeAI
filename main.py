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
    if os.path.exists("frontend/index.html"):
        with open("frontend/index.html", "r", encoding="utf-8") as f:
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
                <p>前端文件未找到，请检查 frontend/index.html 文件是否存在</p>
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
    resume: UploadFile = File(...)
):
    """
    根据职位描述生成简历
    """
    check_modules_available()
    
    try:
        # 保存上传的简历文件
        resume_path = f"uploaded_resume_{int(datetime.now().timestamp())}_{resume.filename}"
        with open(resume_path, "wb") as buffer:
            buffer.write(await resume.read())
        
        # 生成简历
        result = ui.generate_resume_by_description(
            description, 
            resume_path, 
            resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        # 清理上传的文件
        if os.path.exists(resume_path):
            os.remove(resume_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/generate-by-url")
async def generate_by_url(
    url: str = Form(...), 
    resume: UploadFile = File(...)
):
    """
    根据职位链接生成简历
    """
    check_modules_available()
    
    try:
        # 保存上传的简历文件
        resume_path = f"uploaded_resume_{int(datetime.now().timestamp())}_{resume.filename}"
        with open(resume_path, "wb") as buffer:
            buffer.write(await resume.read())
        
        # 生成简历
        result = ui.generate_resume_by_url(
            url, 
            resume_path, 
            resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        # 清理上传的文件
        if os.path.exists(resume_path):
            os.remove(resume_path)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/generate-by-template")
async def generate_by_template(
    template_name: str = Form(...), 
    resume: UploadFile = File(...)
):
    """
    根据模板生成简历
    """
    check_modules_available()
    
    try:
        # 保存上传的简历文件
        resume_path = f"uploaded_resume_{int(datetime.now().timestamp())}_{resume.filename}"
        with open(resume_path, "wb") as buffer:
            buffer.write(await resume.read())
        
        # 生成简历
        result = ui.generate_resume_by_template(
            template_name, 
            resume_path, 
            resume.filename.split('.')[-1] if '.' in resume.filename else 'pdf'
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        # 清理上传的文件
        if os.path.exists(resume_path):
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
            return {"history": history_data.get("history", [])}
        else:
            # 返回模拟历史数据
            return {
                "history": [
                    {
                        "timestamp": "2023-12-01T10:30:00",
                        "type": "description",
                        "match_score": 0.85,
                        "generated_file": "demo_resume_1.pdf"
                    },
                    {
                        "timestamp": "2023-12-01T11:15:00", 
                        "type": "template",
                        "match_score": 0.90,
                        "generated_file": "demo_resume_2.pdf"
                    }
                ]
            }
    except Exception as e:
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
    
    file_path = filename
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="文件未找到")

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
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

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
        user = user_manager.get_user(user_id)
        if user:
            return {
                "success": True,
                "user": user
            }
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
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

@app.post("/users/{user_id}/resumes")
async def create_resume(user_id: str, content: ResumeContent):
    """
    为用户创建简历
    """
    try:
        # 验证用户是否存在
        user = user_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 设置用户ID
        content.user_id = user_id
        content.profile = user  # 使用用户的个人信息
        
        # 创建简历
        resume = user_manager.create_resume(content)
        
        return {
            "success": True,
            "message": "简历创建成功",
            "resume": resume
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建简历失败: {str(e)}")

@app.get("/users/{user_id}/resumes/{resume_id}")
async def get_resume(user_id: str, resume_id: str):
    """
    获取用户简历
    """
    try:
        resume = user_manager.get_resume(resume_id)
        if resume and resume.user_id == user_id:
            return {
                "success": True,
                "resume": resume
            }
        else:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简历失败: {str(e)}")

@app.put("/users/{user_id}/resumes/{resume_id}")
async def update_resume(user_id: str, resume_id: str, content: ResumeContent):
    """
    更新用户简历
    """
    try:
        # 验证简历是否属于用户
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 更新简历
        content.resume_id = resume_id
        content.user_id = user_id
        updated_resume = user_manager.update_resume(content)
        
        return {
            "success": True,
            "message": "简历更新成功",
            "resume": updated_resume
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新简历失败: {str(e)}")

@app.post("/users/{user_id}/resumes/{resume_id}/files")
async def upload_resume_file(user_id: str, resume_id: str, file: UploadFile = File(...)):
    """
    为用户简历上传文件
    """
    check_modules_available()
    
    try:
        # 验证简历是否属于用户
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 保存简历文件
        resume_file = user_manager.save_resume_file(
            resume_id, 
            file_content, 
            file.filename, 
            file.content_type
        )
        
        # 尝试解析简历
        try:
            file_type = file.filename.split('.')[-1] if '.' in file.filename else 'pdf'
            resume_data = ui.resume_parser.parse_resume(resume_file.file_path, file_type)
            user_manager.save_parsed_resume_data(resume_file.file_id, resume_data)
            resume_file.is_parsed = True
        except Exception as parse_error:
            # 解析失败不影响简历上传
            print(f"简历解析失败: {parse_error}")
        
        return {
            "success": True,
            "message": "简历文件上传成功",
            "file": resume_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传简历文件失败: {str(e)}")

@app.get("/users/{user_id}/resumes/{resume_id}/files/{file_id}")
async def get_resume_file(user_id: str, resume_id: str, file_id: str):
    """
    获取简历文件信息
    """
    try:
        # 验证简历是否属于用户
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 获取文件信息
        resume_file = user_manager.get_resume_file(file_id)
        if not resume_file or resume_file.resume_id != resume_id:
            raise HTTPException(status_code=404, detail="文件不存在或不属于该简历")
        
        return {
            "success": True,
            "file": resume_file
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取简历文件信息失败: {str(e)}")

@app.post("/users/{user_id}/resumes/{resume_id}/generate-by-description")
async def generate_by_description(
    user_id: str,
    resume_id: str,
    description: str = Form(...)
):
    """
    根据职位描述为用户生成简历
    """
    check_modules_available()
    
    try:
        # 验证用户和简历
        user = user_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 获取最新的简历文件
        # 在实际应用中，这里应该查询数据库获取最新的简历文件
        # 为简化起见，我们使用一个占位符
        resume_file_path = "placeholder_resume.pdf"
        file_type = "pdf"
        
        # 生成简历
        result = ui.generate_resume_by_description(
            description, 
            resume_file_path, 
            file_type
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/users/{user_id}/resumes/{resume_id}/generate-by-url")
async def generate_by_url(
    user_id: str,
    resume_id: str,
    url: str = Form(...)
):
    """
    根据职位链接为用户生成简历
    """
    check_modules_available()
    
    try:
        # 验证用户和简历
        user = user_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 获取最新的简历文件
        # 在实际应用中，这里应该查询数据库获取最新的简历文件
        # 为简化起见，我们使用一个占位符
        resume_file_path = "placeholder_resume.pdf"
        file_type = "pdf"
        
        # 生成简历
        result = ui.generate_resume_by_url(
            url, 
            resume_file_path, 
            file_type
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.post("/users/{user_id}/resumes/{resume_id}/generate-by-template")
async def generate_by_template(
    user_id: str,
    resume_id: str,
    template_name: str = Form(...)
):
    """
    根据模板为用户生成简历
    """
    check_modules_available()
    
    try:
        # 验证用户和简历
        user = user_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 获取最新的简历文件
        # 在实际应用中，这里应该查询数据库获取最新的简历文件
        # 为简化起见，我们使用一个占位符
        resume_file_path = "placeholder_resume.pdf"
        file_type = "pdf"
        
        # 生成简历
        result = ui.generate_resume_by_template(
            template_name, 
            resume_file_path, 
            file_type
        )
        
        # 添加时间戳
        result["timestamp"] = datetime.now().isoformat()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/users/{user_id}/resumes/{resume_id}/formats/{format}")
async def download_resume(user_id: str, resume_id: str, format: str):
    """
    下载指定格式的简历
    """
    try:
        # 验证用户和简历
        user = user_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        resume = user_manager.get_resume(resume_id)
        if not resume or resume.user_id != user_id:
            raise HTTPException(status_code=404, detail="简历不存在或不属于该用户")
        
        # 获取简历格式信息
        formats = user_manager.get_resume_formats(resume_id)
        if not formats:
            raise HTTPException(status_code=404, detail="未找到指定格式的简历")
        
        # 根据格式返回文件
        file_path = None
        if format == "pdf" and formats.pdf_path:
            file_path = formats.pdf_path
        elif format == "docx" and formats.docx_path:
            file_path = formats.docx_path
        elif format == "html" and formats.html_path:
            file_path = formats.html_path
        else:
            raise HTTPException(status_code=404, detail=f"不支持的格式或未生成该格式: {format}")
        
        if os.path.exists(file_path):
            return FileResponse(file_path, filename=f"resume.{format}")
        else:
            raise HTTPException(status_code=404, detail="文件未找到")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
