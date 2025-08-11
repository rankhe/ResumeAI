"""
用户交互模块
实现多种简历生成方式的统一接口
"""

from typing import Dict, List, Optional
from job_analyzer import JobAnalyzer
from resume_parser import ResumeParser
from resume_optimizer import ResumeOptimizer
from resume_generator import ResumeGenerator
import json
import os
import uuid

class UserInterface:
    def __init__(self):
        self.job_analyzer = JobAnalyzer()
        self.resume_parser = ResumeParser()
        self.resume_optimizer = ResumeOptimizer()
        self.resume_generator = ResumeGenerator()
        self.templates_dir = "templates"
        self.history_file = "generation_history.json"
        
        # 确保模板目录存在
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def generate_resume_by_description(self, job_description: str, resume_file: str, file_type: str = None, user_id: str = None) -> Dict:
        """
        根据职位描述生成简历
        
        Args:
            job_description: 职位描述文本
            resume_file: 简历文件路径
            file_type: 简历文件类型（可选）
            user_id: 用户ID（可选）
            
        Returns:
            生成结果字典
        """
        try:
            # 如果未提供文件类型，则从文件路径推断
            if file_type is None:
                file_type = resume_file.split('.')[-1] if '.' in resume_file else 'pdf'
            
            # 模拟职位信息结构
            job_info = {
                "title": "自定义职位",
                "company": "自定义公司",
                "description": job_description,
                "requirements": self._extract_requirements_from_description(job_description),
                "key_skills": self._extract_skills_from_description(job_description)
            }
            
            # 解析用户简历
            if resume_file:
                resume_data = self.resume_parser.parse_resume(resume_file, file_type)
            else:
                # 如果没有上传简历，尝试从用户资料获取信息
                resume_data = self._get_user_resume_data(user_id)
            
            # 优化简历
            optimization_result = self.resume_optimizer.optimize_resume(job_info, resume_data)
            
            # 生成多种格式的简历
            formats = self._generate_multiple_formats(optimization_result["optimized_content"], job_info, resume_data)
            
            # 保存生成历史
            self._save_to_history({
                "type": "description",
                "input": job_description,
                "output": formats.pdf_path if formats.pdf_path else "generated_resume.pdf",
                "match_score": optimization_result["match_score"]
            })
            
            return {
                "success": True,
                "message": "简历生成成功",
                "match_score": optimization_result["match_score"],
                "suggestions": optimization_result["suggestions"],
                "ats_suggestions": optimization_result["ats_suggestions"],
                "generated_files": {
                    "pdf": formats.pdf_path,
                    "docx": formats.docx_path,
                    "html": formats.html_path
                },
                "formats": {
                    "pdf": formats.pdf_path,
                    "docx": formats.docx_path,
                    "html": formats.html_path
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"简历生成失败: {str(e)}"
            }
    
    def generate_resume_by_url(self, job_url: str, resume_file: str, file_type: str = None, user_id: str = None) -> Dict:
        """
        根据职位链接生成简历
        
        Args:
            job_url: 职位链接
            resume_file: 简历文件路径
            file_type: 简历文件类型（可选）
            
        Returns:
            生成结果字典
        """
        try:
            # 如果未提供文件类型，则从文件路径推断
            if file_type is None:
                file_type = resume_file.split('.')[-1] if '.' in resume_file else 'pdf'
            
            # 分析职位信息
            job_info = self.job_analyzer.analyze_job_posting(job_url)
            
            # 解析用户简历
            if resume_file:
                resume_data = self.resume_parser.parse_resume(resume_file, file_type)
            else:
                # 如果没有上传简历，尝试从用户资料获取信息
                resume_data = self._get_user_resume_data(user_id)
            
            # 优化简历
            optimization_result = self.resume_optimizer.optimize_resume(job_info, resume_data)
            
            # 生成多种格式的简历
            formats = self._generate_multiple_formats(optimization_result["optimized_content"], job_info, resume_data)
            
            # 保存生成历史
            self._save_to_history({
                "type": "url",
                "input": job_url,
                "output": formats.pdf_path if formats.pdf_path else "generated_resume.pdf",
                "match_score": optimization_result["match_score"]
            })
            
            return {
                "success": True,
                "message": "简历生成成功",
                "match_score": optimization_result["match_score"],
                "suggestions": optimization_result["suggestions"],
                "ats_suggestions": optimization_result["ats_suggestions"],
                "generated_files": {
                    "pdf": formats.pdf_path,
                    "docx": formats.docx_path,
                    "html": formats.html_path
                },
                "formats": {
                    "pdf": formats.pdf_path,
                    "docx": formats.docx_path,
                    "html": formats.html_path
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"简历生成失败: {str(e)}"
            }
    
    def generate_resume_by_template(self, template_name: str, resume_file: str, file_type: str = None, user_id: str = None) -> Dict:
        """
        根据模板生成简历
        
        Args:
            template_name: 模板名称
            resume_file: 简历文件路径
            file_type: 简历文件类型（可选）
            
        Returns:
            生成结果字典
        """
        try:
            # 如果未提供文件类型，则从文件路径推断
            if file_type is None:
                file_type = resume_file.split('.')[-1] if '.' in resume_file else 'pdf'
            
            # 检查模板是否存在
            template_path = os.path.join(self.templates_dir, f"{template_name}.json")
            if not os.path.exists(template_path):
                return {
                    "success": False,
                    "message": f"模板 '{template_name}' 不存在"
                }
            
            # 加载模板
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # 解析用户简历
            if resume_file:
                resume_data = self.resume_parser.parse_resume(resume_file, file_type)
            else:
                # 如果没有上传简历，尝试从用户资料获取信息
                resume_data = self._get_user_resume_data(user_id)
            
            # 使用模板数据作为职位信息
            job_info = template_data
            
            # 优化简历
            optimization_result = self.resume_optimizer.optimize_resume(job_info, resume_data)
            
            # 生成多种格式的简历
            formats = self._generate_multiple_formats(optimization_result["optimized_content"], job_info, resume_data)
            
            # 保存生成历史
            self._save_to_history({
                "type": "template",
                "input": template_name,
                "output": formats.pdf_path if formats.pdf_path else "generated_resume.pdf",
                "match_score": optimization_result["match_score"]
            })
            
            return {
                "success": True,
                "message": "简历生成成功",
                "match_score": optimization_result["match_score"],
                "suggestions": optimization_result["suggestions"],
                "ats_suggestions": optimization_result["ats_suggestions"],
                "generated_files": {
                    "pdf": formats.pdf_path,
                    "docx": formats.docx_path,
                    "html": formats.html_path
                },
                "formats": {
                    "pdf": formats.pdf_path,
                    "docx": formats.docx_path,
                    "html": formats.html_path
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"简历生成失败: {str(e)}"
            }
    
    def _generate_multiple_formats(self, optimized_content: str, job_info: Dict, resume_data: Dict) -> 'ResumeFormats':
        """
        生成多种格式的简历
        
        Args:
            optimized_content: 优化后的简历内容
            job_info: 职位信息
            resume_data: 简历数据
            
        Returns:
            包含多种格式路径的ResumeFormats对象
        """
        import uuid
        from models import ResumeFormats
        
        # 生成唯一标识符
        unique_id = uuid.uuid4().hex
        
        # 生成PDF格式
        pdf_path = f"generated_resume_{unique_id}.pdf"
        self.resume_generator.generate_resume(optimized_content, "pdf", f"generated_resume_{unique_id}")
        
        # 生成DOCX格式
        docx_path = f"generated_resume_{unique_id}.docx"
        self.resume_generator.generate_resume(optimized_content, "docx", f"generated_resume_{unique_id}")
        
        # 生成HTML格式
        html_path = f"generated_resume_{unique_id}.html"
        self._generate_html_resume(optimized_content, job_info, resume_data, html_path)
        
        # 创建ResumeFormats对象
        formats = ResumeFormats(
            resume_id=unique_id,
            pdf_path=pdf_path,
            docx_path=docx_path,
            html_path=html_path
        )
        
        return formats
    
    def _generate_html_resume(self, optimized_content: str, job_info: Dict, resume_data: Dict, output_path: str):
        """
        生成HTML格式的简历
        
        Args:
            optimized_content: 优化后的简历内容
            job_info: 职位信息
            resume_data: 简历数据
            output_path: 输出文件路径
        """
        # 创建HTML内容
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>简历 - {job_info.get('title', '未知职位')}</title>
    <style>
        body {{
            font-family: "Microsoft YaHei", "SimHei", "SimSun", Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        h1 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            border-left: 4px solid #3498db;
            padding-left: 10px;
            margin-top: 30px;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .contact-info {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .skill {{
            background-color: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .experience-item, .education-item {{
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .experience-item:last-child, .education-item:last-child {{
            border-bottom: none;
        }}
        .job-title {{
            font-weight: bold;
            color: #3498db;
        }}
        @media print {{
            body {{
                padding: 0;
            }}
            button {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <button onclick="window.print()" style="margin-bottom: 20px; padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">
        打印简历
    </button>
    
    <h1>优化后的简历</h1>
    
    <div class="contact-info">
        <h2>个人信息</h2>
        """
        
        # 添加联系信息
        contact_info = resume_data.get("contact_info", {})
        if contact_info:
            html_content += f"""
        <p><strong>姓名:</strong> {contact_info.get('name', '未提供')}</p>
        <p><strong>邮箱:</strong> {contact_info.get('email', '未提供')}</p>
        <p><strong>电话:</strong> {contact_info.get('phone', '未提供')}</p>
        """
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>针对职位</h2>
        <p><strong>职位:</strong> """ + job_info.get('title', '未知职位') + """</p>
        <p><strong>公司:</strong> """ + job_info.get('company', '未知公司') + """</p>
    </div>
    
    <div class="section">
        <h2>核心技能</h2>
        <div class="skills">
        """
        
        # 添加技能
        skills = resume_data.get("skills", [])
        for skill in skills:
            html_content += f'<span class="skill">{skill}</span>\n'
        
        html_content += """
        </div>
    </div>
    
    <div class="section">
        <h2>工作经历</h2>
        """
        
        # 添加工作经历
        experiences = resume_data.get("work_experience", [])
        for exp in experiences:
            if isinstance(exp, dict):
                html_content += f"""
        <div class="experience-item">
            <p><span class="job-title">{exp.get('title', '未知职位')}</span> - {exp.get('company', '未知公司')}</p>
            <p>{exp.get('description', '')}</p>
        </div>
                """
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>教育背景</h2>
        """
        
        # 添加教育背景
        educations = resume_data.get("education", [])
        for edu in educations:
            if isinstance(edu, dict):
                html_content += f"""
        <div class="education-item">
            <p><strong>{edu.get('institution', '未知院校')}</strong> - {edu.get('degree', '未知学位')}</p>
        </div>
                """
        
        html_content += """
    </div>
    
    <div class="section">
        <h2>优化建议</h2>
        <h3>匹配度评分: """ + str(self.resume_optimizer._calculate_match_score(job_info, resume_data)) + """%</h3>
        """
        
        # 添加优化建议
        suggestions = self.resume_optimizer._generate_suggestions(job_info, resume_data)
        if suggestions:
            html_content += "<ul>\n"
            for suggestion in suggestions:
                html_content += f"            <li>{suggestion}</li>\n"
            html_content += "        </ul>\n"
        
        html_content += """
    </div>
    
    <script>
        // 页面加载完成后提示用户可以打印
        window.onload = function() {
            if (window.matchMedia('print').matches) {
                // 打印模式下不显示按钮
            } else {
                // 屏幕显示模式下保持按钮可见
            }
        }
    </script>
</body>
</html>
        """
        
        # 保存HTML文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def get_available_templates(self) -> List[str]:
        """
        获取可用的简历模板列表
        
        Returns:
            模板名称列表
        """
        templates = []
        if os.path.exists(self.templates_dir):
            for file in os.listdir(self.templates_dir):
                if file.endswith('.json'):
                    templates.append(file[:-5])  # 移除.json后缀
        return templates
    
    def create_template(self, template_name: str, template_data: Dict) -> bool:
        """
        创建新的简历模板
        
        Args:
            template_name: 模板名称
            template_data: 模板数据
            
        Returns:
            是否创建成功
        """
        try:
            template_path = os.path.join(self.templates_dir, f"{template_name}.json")
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def get_generation_history(self) -> List[Dict]:
        """
        获取生成历史记录
        
        Returns:
            历史记录列表
        """
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
    
    def _extract_requirements_from_description(self, description: str) -> List[str]:
        """
        从职位描述中提取要求
        
        Args:
            description: 职位描述
            
        Returns:
            要求列表
        """
        # 简单实现，实际应用中可以使用NLP技术
        requirements = []
        
        # 常见要求关键词
        keywords = ['经验', '技能', '能力', '学历', '资格']
        sentences = description.split('。')
        
        for sentence in sentences:
            for keyword in keywords:
                if keyword in sentence:
                    requirements.append(sentence.strip())
                    break
        
        return requirements if requirements else ["未明确列出具体要求"]
    
    def _extract_skills_from_description(self, description: str) -> List[str]:
        """
        从职位描述中提取技能要求
        
        Args:
            description: 职位描述
            
        Returns:
            技能列表
        """
        # 常见技能关键词
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Angular',
            'Node.js', 'Express', 'Django', 'Flask', 'Spring',
            'SQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'AWS', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'AI', '数据分析', '云计算'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in description.lower():
                found_skills.append(skill)
        
        return found_skills
    
    def _get_user_resume_data(self, user_id: str = None) -> Dict:
        """
        从用户资料获取简历数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            简历数据字典
        """
        if user_id:
            try:
                from models import UserResumeManager
                user_manager = UserResumeManager()
                user_profile = user_manager.get_user(user_id)
                
                if user_profile:
                    # 将用户资料转换为简历数据格式
                    skills = []
                    if hasattr(user_profile, 'skills') and user_profile.skills:
                        if isinstance(user_profile.skills, str):
                            skills = [skill.strip() for skill in user_profile.skills.split(',') if skill.strip()]
                        elif isinstance(user_profile.skills, list):
                            skills = user_profile.skills
                    
                    return {
                        "contact_info": {
                            "name": user_profile.name or "待填写",
                            "email": user_profile.email or "待填写",
                            "phone": user_profile.phone or "待填写",
                            "address": getattr(user_profile, 'address', '') or "",
                            "gender": getattr(user_profile, 'gender', '') or ""
                        },
                        "skills": skills,
                        "work_experience": [],  # 可以后续扩展
                        "education": [],  # 可以后续扩展
                        "projects": [],
                        "summary": getattr(user_profile, 'summary', '') or "",
                        "education_level": getattr(user_profile, 'education_level', '') or "",
                        "work_experience_years": getattr(user_profile, 'work_experience', '') or ""
                    }
            except Exception as e:
                print(f"获取用户资料失败: {e}")
        
        # 如果没有用户ID或获取失败，返回默认空数据
        return {
            "contact_info": {
                "name": "待填写",
                "email": "待填写",
                "phone": "待填写"
            },
            "skills": [],
            "work_experience": [],
            "education": [],
            "projects": []
        }
    
    def _save_to_history(self, record: Dict):
        """
        保存生成记录到历史文件
        
        Args:
            record: 记录数据
        """
        try:
            # 添加时间戳
            import datetime
            record["timestamp"] = datetime.datetime.now().isoformat()
            
            history = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            history.append(record)
            
            # 只保留最近100条记录
            if len(history) > 100:
                history = history[-100:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception:
            # 如果保存失败，不抛出异常，不影响主功能
            pass

# 使用示例
if __name__ == "__main__":
    ui = UserInterface()
    
    # 创建示例模板
    template_data = {
        "title": "软件工程师",
        "company": "模板公司",
        "description": "负责软件开发工作",
        "requirements": ["熟悉Python", "了解Django框架", "有数据库经验"],
        "key_skills": ["Python", "Django", "MySQL"]
    }
    ui.create_template("software_engineer", template_data)
    
    print("可用模板:", ui.get_available_templates())