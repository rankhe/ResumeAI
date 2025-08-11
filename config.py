import os
from typing import Dict, List

class Config:
    """应用配置类"""
    
    # 基础配置
    APP_NAME = "AI简历助手"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # 服务器配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # 文件配置
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['.pdf', '.docx']
    UPLOAD_DIR = "uploads"
    OUTPUT_DIR = "outputs"
    TEMPLATES_DIR = "templates"
    
    # 简历解析配置
    RESUME_PARSING = {
        "max_text_length": 50000,
        "min_text_length": 100,
        "supported_languages": ["zh", "en"],
        "extract_sections": [
            "contact_info",
            "work_experience", 
            "education",
            "skills",
            "projects",
            "certifications"
        ]
    }
    
    # 职位分析配置
    JOB_ANALYSIS = {
        "request_timeout": 30,
        "max_retries": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "supported_sites": [
            "linkedin.com",
            "zhaopin.com", 
            "51job.com",
            "lagou.com",
            "boss.com"
        ]
    }
    
    # 简历优化配置
    OPTIMIZATION = {
        "min_match_score": 0.3,
        "max_suggestions": 10,
        "skill_weight": 0.3,
        "experience_weight": 0.25,
        "education_weight": 0.15,
        "project_weight": 0.2,
        "keyword_weight": 0.1,
        "ats_keywords": [
            "responsible for", "managed", "developed", "implemented",
            "achieved", "improved", "created", "designed", "led",
            "负责", "管理", "开发", "实现", "达成", "改进", "创建", "设计", "领导"
        ]
    }
    
    # 简历生成配置
    GENERATION = {
        "default_format": "pdf",
        "supported_formats": ["pdf", "docx"],
        "pdf_settings": {
            "page_size": "A4",
            "margin": 72,  # 1 inch
            "font_size": 11,
            "line_spacing": 1.2
        },
        "docx_settings": {
            "font_name": "Arial",
            "font_size": 11,
            "line_spacing": 1.15
        }
    }
    
    # 模板配置
    TEMPLATES = {
        "default_templates": [
            "software_engineer",
            "data_analyst", 
            "product_manager",
            "marketing_specialist",
            "sales_representative"
        ],
        "template_fields": [
            "title",
            "company", 
            "description",
            "requirements",
            "key_skills",
            "preferred_qualifications"
        ]
    }
    
    # 历史记录配置
    HISTORY = {
        "max_records": 1000,
        "auto_cleanup": True,
        "cleanup_days": 30,
        "backup_enabled": True
    }
    
    # 安全配置
    SECURITY = {
        "allowed_hosts": ["*"],
        "cors_origins": ["*"],
        "max_request_size": 50 * 1024 * 1024,  # 50MB
        "rate_limit": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000
        }
    }
    
    # 日志配置
    LOGGING = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "app.log",
        "max_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
    
    # 技能关键词库
    SKILL_KEYWORDS = {
        "programming_languages": [
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", 
            "Rust", "Swift", "Kotlin", "PHP", "Ruby", "Scala", "R", "MATLAB"
        ],
        "web_technologies": [
            "HTML", "CSS", "React", "Vue", "Angular", "Node.js", "Express",
            "Django", "Flask", "Spring", "Laravel", "Rails", "ASP.NET"
        ],
        "databases": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
            "SQL Server", "Elasticsearch", "Cassandra", "DynamoDB"
        ],
        "cloud_platforms": [
            "AWS", "Azure", "Google Cloud", "阿里云", "腾讯云", "华为云",
            "Docker", "Kubernetes", "Terraform", "Ansible"
        ],
        "data_science": [
            "Machine Learning", "Deep Learning", "Data Analysis", "Statistics",
            "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
            "Tableau", "Power BI", "Jupyter", "数据分析", "机器学习"
        ],
        "tools": [
            "Git", "GitHub", "GitLab", "JIRA", "Confluence", "Jenkins",
            "Travis CI", "CircleCI", "Slack", "Trello", "Notion"
        ]
    }
    
    @classmethod
    def get_all_skills(cls) -> List[str]:
        """获取所有技能关键词"""
        all_skills = []
        for category in cls.SKILL_KEYWORDS.values():
            all_skills.extend(category)
        return list(set(all_skills))
    
    @classmethod
    def get_config_dict(cls) -> Dict:
        """获取配置字典"""
        config = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and not callable(getattr(cls, attr_name)):
                config[attr_name] = getattr(cls, attr_name)
        return config
    
    @classmethod
    def validate_config(cls) -> bool:
        """验证配置有效性"""
        try:
            # 检查必要目录
            for directory in [cls.UPLOAD_DIR, cls.OUTPUT_DIR, cls.TEMPLATES_DIR]:
                os.makedirs(directory, exist_ok=True)
            
            # 检查文件大小限制
            if cls.MAX_FILE_SIZE <= 0:
                raise ValueError("MAX_FILE_SIZE must be positive")
            
            # 检查端口范围
            if not (1 <= cls.PORT <= 65535):
                raise ValueError("PORT must be between 1 and 65535")
            
            return True
        except Exception as e:
            print(f"配置验证失败: {e}")
            return False

# 环境特定配置
class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    LOGGING = {
        **Config.LOGGING,
        "level": "DEBUG"
    }

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SECURITY = {
        **Config.SECURITY,
        "allowed_hosts": ["localhost", "127.0.0.1"],
        "cors_origins": ["http://localhost:3000", "https://yourdomain.com"]
    }

class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    UPLOAD_DIR = "test_uploads"
    OUTPUT_DIR = "test_outputs"
    TEMPLATES_DIR = "test_templates"

# 根据环境变量选择配置
def get_config():
    """根据环境变量获取配置类"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig
    elif env == "testing":
        return TestingConfig
    else:
        return DevelopmentConfig

# 导出当前配置
current_config = get_config()