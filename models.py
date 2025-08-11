"""
用户和简历数据模型
遵循行业通用的简历设计标准
"""

from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json
import os

class UserProfile(BaseModel):
    """用户基本信息模型 - 简历必需信息"""
    user_id: Optional[str] = None
    name: str = Field(default="匿名用户", description="姓名")
    email: str = Field(default="", description="电子邮箱")
    phone: str = Field(default="", description="电话号码")
    gender: str = Field(default="未指定", description="性别")
    photo: str = Field(default="", description="照片文件路径")
    address: str = Field(default="", description="地址")
    website: str = Field(default="", description="个人网站/LinkedIn")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class WorkExperience(BaseModel):
    """工作经历模型"""
    id: Optional[str] = None
    company: str = Field(description="公司名称")
    position: str = Field(description="职位")
    start_date: str = Field(description="开始日期")
    end_date: str = Field(default="至今", description="结束日期")
    is_current: bool = Field(default=False, description="是否为当前工作")
    description: str = Field(default="", description="工作描述")
    achievements: List[str] = Field(default=[], description="主要成就")

class Education(BaseModel):
    """教育背景模型"""
    id: Optional[str] = None
    institution: str = Field(description="学校/机构名称")
    degree: str = Field(description="学位")
    field_of_study: str = Field(default="", description="专业")
    start_date: str = Field(description="开始日期")
    end_date: str = Field(default="", description="结束日期")
    gpa: Optional[float] = Field(default=None, description="GPA")
    description: str = Field(default="", description="描述")

class Skill(BaseModel):
    """技能模型"""
    id: Optional[str] = None
    name: str = Field(description="技能名称")
    proficiency: str = Field(default="中级", description="熟练程度")
    category: str = Field(default="其他", description="技能类别")

class Certificate(BaseModel):
    """证书模型"""
    id: Optional[str] = None
    name: str = Field(description="证书名称")
    issuing_organization: str = Field(description="颁发机构")
    issue_date: str = Field(description="颁发日期")
    expiration_date: Optional[str] = Field(default=None, description="过期日期")
    credential_id: str = Field(default="", description="证书编号")

class Project(BaseModel):
    """项目经历模型"""
    id: Optional[str] = None
    name: str = Field(description="项目名称")
    description: str = Field(description="项目描述")
    start_date: str = Field(description="开始日期")
    end_date: str = Field(default="", description="结束日期")
    role: str = Field(default="", description="担任角色")
    technologies: List[str] = Field(default=[], description="使用技术")
    url: str = Field(default="", description="项目链接")
    achievements: List[str] = Field(default=[], description="项目成果")

class Language(BaseModel):
    """语言能力模型"""
    id: Optional[str] = None
    name: str = Field(description="语言名称")
    proficiency: str = Field(default="中级", description="熟练程度")
    certificate: str = Field(default="", description="相关证书")

class ResumeBaseInfo(BaseModel):
    """简历基本信息模型"""
    resume_id: Optional[str] = None
    user_id: Optional[str] = None
    title: str = Field(default="个人简历", description="简历标题")
    summary: str = Field(default="", description="个人简介/职业摘要")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ResumeContent(BaseModel):
    """简历内容模型 - 遵循行业标准结构"""
    # 必需信息
    profile: UserProfile = Field(description="用户基本信息")
    work_experience: List[WorkExperience] = Field(default=[], description="工作经历")
    
    # 可选信息
    education: List[Education] = Field(default=[], description="教育背景")
    skills: List[Skill] = Field(default=[], description="技能")
    certificates: List[Certificate] = Field(default=[], description="证书")
    projects: List[Project] = Field(default=[], description="项目经历")
    languages: List[Language] = Field(default=[], description="语言能力")
    
    # 其他可选信息
    interests: List[str] = Field(default=[], description="兴趣爱好")
    references: str = Field(default="", description="推荐人信息")
    custom_sections: Dict[str, str] = Field(default={}, description="自定义部分")

class ResumeFile(BaseModel):
    """简历文件模型"""
    file_id: Optional[str] = None
    resume_id: str = Field(description="关联的简历ID")
    file_path: str = Field(description="文件路径")
    file_type: str = Field(description="文件类型: pdf, docx, html")
    original_name: str = Field(description="原始文件名")
    uploaded_at: datetime = Field(default_factory=datetime.now)
    is_parsed: bool = Field(default=False, description="是否已解析")

class ResumeFormats(BaseModel):
    """简历多格式支持模型"""
    formats_id: Optional[str] = None
    resume_id: str = Field(description="关联的简历ID")
    pdf_path: Optional[str] = Field(default=None, description="PDF格式路径")
    docx_path: Optional[str] = Field(default=None, description="DOCX格式路径")
    html_path: Optional[str] = Field(default=None, description="HTML格式路径")
    generated_at: datetime = Field(default_factory=datetime.now)

class UserResumeManager:
    """用户简历管理器"""
    
    def __init__(self, data_dir: str = "user_data"):
        self.data_dir = data_dir
        self.users_dir = os.path.join(data_dir, "users")
        self.resumes_dir = os.path.join(data_dir, "resumes")
        self.files_dir = os.path.join(data_dir, "files")
        
        # 创建必要的目录
        os.makedirs(self.users_dir, exist_ok=True)
        os.makedirs(self.resumes_dir, exist_ok=True)
        os.makedirs(self.files_dir, exist_ok=True)
    
    def create_user(self, profile: UserProfile) -> UserProfile:
        """创建用户"""
        if not profile.user_id:
            import uuid
            profile.user_id = str(uuid.uuid4())
        
        profile.created_at = datetime.now()
        profile.updated_at = datetime.now()
        
        # 保存用户信息
        user_file = os.path.join(self.users_dir, f"{profile.user_id}.json")
        with open(user_file, 'w', encoding='utf-8') as f:
            f.write(profile.json())
        
        return profile
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """获取用户信息"""
        user_file = os.path.join(self.users_dir, f"{user_id}.json")
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return UserProfile(**data)
        return None
    
    def update_user(self, profile: UserProfile) -> UserProfile:
        """更新用户信息"""
        profile.updated_at = datetime.now()
        
        user_file = os.path.join(self.users_dir, f"{profile.user_id}.json")
        with open(user_file, 'w', encoding='utf-8') as f:
            f.write(profile.json())
        
        return profile
    
    def create_resume(self, content: ResumeContent) -> ResumeContent:
        """创建简历"""
        if not content.resume_id:
            import uuid
            content.resume_id = str(uuid.uuid4())
        
        content.created_at = datetime.now()
        content.updated_at = datetime.now()
        
        # 保存简历内容
        resume_file = os.path.join(self.resumes_dir, f"{content.resume_id}.json")
        with open(resume_file, 'w', encoding='utf-8') as f:
            f.write(content.json())
        
        return content
    
    def get_resume(self, resume_id: str) -> Optional[ResumeContent]:
        """获取简历内容"""
        resume_file = os.path.join(self.resumes_dir, f"{resume_id}.json")
        if os.path.exists(resume_file):
            with open(resume_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ResumeContent(**data)
        return None
    
    def update_resume(self, content: ResumeContent) -> ResumeContent:
        """更新简历内容"""
        content.updated_at = datetime.now()
        
        resume_file = os.path.join(self.resumes_dir, f"{content.resume_id}.json")
        with open(resume_file, 'w', encoding='utf-8') as f:
            f.write(content.json())
        
        return content
    
    def save_resume_file(self, resume_id: str, file_content: bytes, original_name: str, file_type: str) -> ResumeFile:
        """保存简历文件"""
        import uuid
        file_id = str(uuid.uuid4())
        
        # 生成文件路径
        file_extension = original_name.split('.')[-1] if '.' in original_name else file_type
        file_path = os.path.join(self.files_dir, f"{file_id}.{file_extension}")
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 创建文件信息
        resume_file = ResumeFile(
            file_id=file_id,
            resume_id=resume_id,
            file_path=file_path,
            file_type=file_type,
            original_name=original_name
        )
        
        # 保存文件信息
        file_info_path = os.path.join(self.files_dir, f"{file_id}.json")
        with open(file_info_path, 'w', encoding='utf-8') as f:
            f.write(resume_file.json())
        
        return resume_file
    
    def get_resume_file(self, file_id: str) -> Optional[ResumeFile]:
        """获取简历文件信息"""
        file_info_path = os.path.join(self.files_dir, f"{file_id}.json")
        if os.path.exists(file_info_path):
            with open(file_info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return ResumeFile(**data)
        return None
    
    def save_parsed_resume_data(self, file_id: str, parsed_data: Dict) -> bool:
        """保存解析后的简历数据到文件"""
        file_info_path = os.path.join(self.files_dir, f"{file_id}.json")
        if os.path.exists(file_info_path):
            with open(file_info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                resume_file = ResumeFile(**data)
            
            # 保存解析数据到单独的文件
            parsed_data_path = os.path.join(self.files_dir, f"{file_id}_parsed.json")
            with open(parsed_data_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
            return True
        return False
    
    def get_parsed_resume_data(self, file_id: str) -> Optional[Dict]:
        """获取解析后的简历数据"""
        parsed_data_path = os.path.join(self.files_dir, f"{file_id}_parsed.json")
        if os.path.exists(parsed_data_path):
            with open(parsed_data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def save_resume_formats(self, resume_id: str, formats: ResumeFormats) -> bool:
        """保存简历多格式版本"""
        if not formats.formats_id:
            import uuid
            formats.formats_id = str(uuid.uuid4())
        
        formats.resume_id = resume_id
        formats.generated_at = datetime.now()
        
        formats_file = os.path.join(self.files_dir, f"{formats.formats_id}_formats.json")
        with open(formats_file, 'w', encoding='utf-8') as f:
            f.write(formats.json())
        return True
    
    def get_resume_formats(self, resume_id: str) -> Optional[ResumeFormats]:
        """获取简历多格式版本"""
        # 查找与简历ID关联的格式信息
        for filename in os.listdir(self.files_dir):
            if filename.endswith('_formats.json'):
                formats_file = os.path.join(self.files_dir, filename)
                with open(formats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    formats = ResumeFormats(**data)
                    if formats.resume_id == resume_id:
                        return formats
        return None

# 使用示例
if __name__ == "__main__":
    # 创建用户简历管理器
    manager = UserResumeManager()
    
    # 创建用户
    user_profile = UserProfile(
        name="张三",
        email="zhangsan@example.com",
        phone="13800138000",
        gender="男"
    )
    
    user = manager.create_user(user_profile)
    print(f"创建用户: {user.name}, ID: {user.user_id}")