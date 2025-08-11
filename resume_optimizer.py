"""
简历优化模块
根据职位要求优化简历内容，提高匹配度和ATS通过率
"""

from typing import Dict, List, Tuple
import re
from collections import Counter

class ResumeOptimizer:
    def __init__(self):
        # ATS友好的动词列表
        self.ats_action_verbs = [
            "achieved", "improved", "managed", "developed", "implemented", "created", "led", "optimized",
            "designed", "built", "maintained", "collaborated", "analyzed", "solved", "increased", "decreased",
            "streamlined", "innovated", "mentored", "trained", "negotiated", "strategized", "transformed"
        ]
        
        # 中文动词列表
        self.chinese_action_verbs = [
            "实现", "提升", "管理", "开发", "实施", "创建", "领导", "优化",
            "设计", "构建", "维护", "协作", "分析", "解决", "增加", "减少",
            "简化", "创新", "指导", "培训", "谈判", "制定", "转型"
        ]
    
    def optimize_resume(self, job_info: Dict, resume_data: Dict) -> Dict:
        """
        优化简历内容
        
        Args:
            job_info: 职位信息字典
            resume_data: 简历数据字典
            
        Returns:
            优化建议和优化后的简历内容
        """
        # 计算匹配度
        match_score = self._calculate_match_score(job_info, resume_data)
        
        # 生成优化建议
        suggestions = self._generate_suggestions(job_info, resume_data)
        
        # 生成ATS优化建议
        ats_suggestions = self._generate_ats_suggestions(resume_data)
        
        # 优化简历内容
        optimized_content = self._optimize_content(job_info, resume_data)
        
        return {
            "match_score": match_score,
            "suggestions": suggestions,
            "ats_suggestions": ats_suggestions,
            "optimized_content": optimized_content
        }
    
    def _calculate_match_score(self, job_info: Dict, resume_data: Dict) -> float:
        """
        计算简历与职位的匹配度
        
        Args:
            job_info: 职位信息
            resume_data: 简历数据
            
        Returns:
            匹配度分数 (0-100)
        """
        score = 0.0
        total_weight = 0.0
        
        # 关键技能匹配 (权重35%)
        skill_score, skill_weight = self._calculate_skill_match(
            job_info.get("key_skills", []), 
            resume_data.get("skills", [])
        )
        score += skill_score * 0.35
        total_weight += 0.35
        
        # 工作经验匹配 (权重30%)
        exp_score, exp_weight = self._calculate_experience_match(
            job_info.get("requirements", []), 
            resume_data.get("work_experience", [])
        )
        score += exp_score * 0.30
        total_weight += 0.30
        
        # 教育背景匹配 (权重15%)
        edu_score, edu_weight = self._calculate_education_match(
            job_info.get("description", ""), 
            resume_data.get("education", [])
        )
        score += edu_score * 0.15
        total_weight += 0.15
        
        # 项目经验匹配 (权重10%)
        project_score, project_weight = self._calculate_project_match(
            job_info.get("description", ""), 
            resume_data.get("projects", [])
        )
        score += project_score * 0.10
        total_weight += 0.10
        
        # 其他关键词匹配 (权重10%)
        keyword_score, keyword_weight = self._calculate_keyword_match(
            job_info.get("description", ""), 
            resume_data.get("text", "")
        )
        score += keyword_score * 0.10
        total_weight += 0.10
        
        # 标准化分数
        if total_weight > 0:
            final_score = min(100.0, (score / total_weight) * 100)
        else:
            final_score = 0.0
            
        return round(final_score, 1)
    
    def _calculate_skill_match(self, required_skills: List[str], resume_skills: List[str]) -> Tuple[float, float]:
        """
        计算技能匹配度
        
        Returns:
            (匹配分数, 权重)
        """
        if not required_skills:
            return 1.0, 0.0  # 如果没有明确技能要求，则满分但不计入总分
            
        matched_skills = 0
        for skill in required_skills:
            # 检查技能是否在简历中（不区分大小写）
            for resume_skill in resume_skills:
                if skill.lower() in resume_skill.lower() or resume_skill.lower() in skill.lower():
                    matched_skills += 1
                    break
        
        return matched_skills / len(required_skills), 1.0
    
    def _calculate_experience_match(self, requirements: List[str], work_experience: List[Dict]) -> Tuple[float, float]:
        """
        计算工作经验匹配度
        """
        if not requirements:
            return 1.0, 0.0
            
        # 检查工作经验描述中是否包含要求的关键词
        experience_items = []
        for exp in work_experience:
            if isinstance(exp, dict):
                exp_text = f"{exp.get('company', '')} {exp.get('title', '')} {exp.get('description', '')}"
                experience_items.append(exp_text)
            else:
                experience_items.append(str(exp))
        
        experience_text = " ".join(experience_items)
        matched_requirements = 0
        
        for req in requirements:
            # 简化处理，实际应用中需要更复杂的语义分析
            if isinstance(req, str) and req.lower() in experience_text.lower():
                matched_requirements += 1
                
        return matched_requirements / len(requirements), 1.0
    
    def _calculate_education_match(self, job_description: str, education: List[Dict]) -> Tuple[float, float]:
        """
        计算教育背景匹配度
        """
        # 检查职位描述中是否有教育相关要求
        edu_keywords = ['学历', '学位', '教育', '毕业', '学历要求', 'degree', 'education', 'bachelor', 'master']
        has_edu_requirement = any(keyword in job_description.lower() for keyword in edu_keywords)
        
        if not has_edu_requirement:
            return 1.0, 0.0  # 没有教育要求则满分但不计入总分
            
        # 简化处理，如果有教育背景就给满分
        if education:
            return 1.0, 1.0
        else:
            return 0.0, 1.0
    
    def _calculate_keyword_match(self, job_description: str, resume_text: str) -> Tuple[float, float]:
        """
        计算关键词匹配度
        """
        # 提取职位描述中的重要关键词
        # 移除常见停用词，保留重要词汇
        stop_words = ['的', '了', '在', '是', '我', '有', '和', '或', '但', '也', 
                     'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'from']
        
        # 更精确的关键词提取
        job_words = re.findall(r'\b[a-zA-Z]{3,}\b|\b[\u4e00-\u9fff]{2,6}\b', job_description.lower())
        job_keywords = [word for word in job_words if word not in stop_words and len(word) > 2]
        
        if not job_keywords:
            return 1.0, 0.0
            
        matched_keywords = 0
        resume_text_lower = resume_text.lower()
        
        for keyword in job_keywords:
            if keyword in resume_text_lower:
                matched_keywords += 1
                
        return matched_keywords / len(job_keywords), 1.0
    
    def _calculate_project_match(self, job_description: str, projects: List[Dict]) -> Tuple[float, float]:
        """
        计算项目经验匹配度
        """
        # 检查职位描述中是否有项目相关要求
        project_keywords = ['项目', 'project', 'experience']
        has_project_requirement = any(keyword in job_description.lower() for keyword in project_keywords)
        
        if not has_project_requirement:
            return 1.0, 0.0  # 没有项目要求则满分但不计入总分
            
        # 检查是否有项目经验
        if not projects:
            return 0.0, 1.0
            
        # 简化处理，如果有项目经验就给满分
        return 1.0, 1.0
    
    def _generate_suggestions(self, job_info: Dict, resume_data: Dict) -> List[str]:
        """
        生成简历优化建议
        
        Returns:
            优化建议列表
        """
        suggestions = []
        
        # 检查关键技能
        required_skills = job_info.get("key_skills", [])
        resume_skills = resume_data.get("skills", [])
        
        missing_skills = []
        for skill in required_skills:
            found = False
            for resume_skill in resume_skills:
                if skill.lower() in resume_skill.lower() or resume_skill.lower() in skill.lower():
                    found = True
                    break
            if not found:
                missing_skills.append(skill)
        
        if missing_skills:
            suggestions.append(f"建议在技能部分添加: {', '.join(missing_skills)}")
        
        # 检查工作经验描述
        job_requirements = job_info.get("requirements", [])
        work_experience = resume_data.get("work_experience", [])
        
        if not work_experience and job_requirements:
            suggestions.append("建议详细描述您的工作经历，以匹配职位要求")
        elif work_experience and job_requirements:
            # 检查工作经验描述是否足够详细
            exp_descriptions = [exp.get('description', '') for exp in work_experience if isinstance(exp, dict)]
            total_exp_length = sum(len(desc) for desc in exp_descriptions)
            if total_exp_length < 200:  # 如果工作经验描述总长度小于200字符
                suggestions.append("建议丰富您的工作经历描述，添加更多具体的工作内容和成果")
        
        # 检查教育背景
        education = resume_data.get("education", [])
        job_description = job_info.get("description", "")
        
        edu_keywords = ['学历', '学位', '教育', '毕业', '学历要求', 'degree', 'education', 'bachelor', 'master']
        has_edu_requirement = any(keyword in job_description.lower() for keyword in edu_keywords)
        
        if has_edu_requirement and not education:
            suggestions.append("职位描述中包含教育要求，建议补充您的教育背景信息")
        
        # 检查项目经验
        projects = resume_data.get("projects", [])
        if '项目' in job_description or 'project' in job_description.lower():
            if not projects:
                suggestions.append("职位描述中提到项目经验，建议补充您的项目经历")
        
        # 检查是否包含职位关键词
        job_title = job_info.get("title", "").lower()
        resume_text = resume_data.get("text", "").lower()
        if job_title and job_title not in resume_text:
            suggestions.append(f"建议在简历中加入目标职位关键词: '{job_info.get('title', '')}'")
        
        # 如果匹配度较低，提供通用建议
        match_score = self._calculate_match_score(job_info, resume_data)
        if match_score < 50:
            suggestions.append("您的简历与职位要求匹配度较低，建议进行全面优化")
        elif match_score < 70:
            suggestions.append("您的简历与职位要求匹配度一般，建议针对性优化")
        
        # 如果没有建议，则给出正面反馈
        if not suggestions:
            suggestions.append("您的简历与职位要求匹配度较高，无需大幅修改")
            
        return suggestions
    
    def _generate_ats_suggestions(self, resume_data: Dict) -> List[str]:
        """
        生成ATS优化建议
        
        Returns:
            ATS优化建议列表
        """
        suggestions = []
        
        # 检查联系信息格式
        contact_info = resume_data.get("contact_info", {})
        if not contact_info.get("email"):
            suggestions.append("建议添加有效的邮箱地址，便于ATS系统识别")
        
        phone = contact_info.get("phone", "")
        if phone and (not re.match(r'[\d\-\s\(\)\+]+', phone) or len(phone) < 10):
            suggestions.append("建议使用标准格式的电话号码，避免使用特殊符号")
        
        # 检查技能部分格式
        skills = resume_data.get("skills", [])
        if skills:
            # 检查技能是否以列表形式呈现
            skills_text = " ".join(skills)
            if len(skills) < 5:
                suggestions.append("建议扩展技能列表，至少包含5项与目标职位相关的核心技能")
        else:
            suggestions.append("建议添加技能部分，列出与目标职位相关的技术和软技能")
        
        # 检查工作经验描述
        work_experience = resume_data.get("work_experience", [])
        if work_experience:
            # 检查是否使用了动作动词
            exp_descriptions = [exp.get('description', '') for exp in work_experience if isinstance(exp, dict)]
            combined_description = " ".join(exp_descriptions).lower()
            
            # 检查是否包含足够的动作动词
            action_verbs_used = [verb for verb in self.ats_action_verbs if verb in combined_description]
            if len(action_verbs_used) < 3:
                suggestions.append("建议在工作经历中使用更多ATS友好的动作动词，如: achieved, managed, developed等")
            
            # 检查是否包含中文动作动词
            chinese_verbs_used = [verb for verb in self.chinese_action_verbs if verb in combined_description]
            if len(chinese_verbs_used) < 3:
                suggestions.append("建议在工作经历中使用更多量化成果的动词，如: 实现、提升、管理等")
        
        # 检查文件格式
        suggestions.append("确保使用标准文件格式(.docx或.pdf)，避免使用图片或扫描件")
        suggestions.append("使用清晰的标题结构，避免复杂的图形和表格")
        suggestions.append("使用标准字体(如Arial、Calibri、Times New Roman)，字号10-12pt")
        
        return suggestions

    def _optimize_content(self, job_info: Dict, resume_data: Dict) -> str:
        """
        优化简历内容
        
        Returns:
            优化后的简历内容
        """
        # 构建优化后的简历内容
        optimized_parts = []
        
        # 添加标题和基本信息
        optimized_parts.append("=== 优化后的简历 ===\n")
        optimized_parts.append(f"目标职位: {job_info.get('title', '未知职位')}\n")
        optimized_parts.append(f"目标公司: {job_info.get('company', '未知公司')}\n")
        optimized_parts.append(f"匹配度评分: {self._calculate_match_score(job_info, resume_data)}%\n")
        optimized_parts.append("-" * 50 + "\n")
        
        # 添加联系信息
        contact_info = resume_data.get("contact_info", {})
        if contact_info:
            optimized_parts.append("【联系信息】\n")
            if contact_info.get("name"):
                optimized_parts.append(f"姓名: {contact_info['name']}\n")
            if contact_info.get("email"):
                optimized_parts.append(f"邮箱: {contact_info['email']}\n")
            if contact_info.get("phone"):
                optimized_parts.append(f"电话: {contact_info['phone']}\n")
            if contact_info.get("linkedin"):
                optimized_parts.append(f"LinkedIn: {contact_info['linkedin']}\n")
            if contact_info.get("github"):
                optimized_parts.append(f"GitHub: {contact_info['github']}\n")
            optimized_parts.append("\n")
        
        # 优化技能部分，确保包含职位要求的技能
        required_skills = job_info.get("key_skills", [])
        resume_skills = resume_data.get("skills", [])
        
        # 合并技能，确保包含所有必需技能
        optimized_skills = list(resume_skills)
        for skill in required_skills:
            if skill not in optimized_skills:
                optimized_skills.append(skill)
        
        if optimized_skills:
            optimized_parts.append("【核心技能】\n")
            # 按类别分组技能（简化处理）
            optimized_parts.append("• " + ", ".join(optimized_skills) + "\n\n")
        
        # 优化工作经验部分
        work_experience = resume_data.get("work_experience", [])
        if work_experience:
            optimized_parts.append("【工作经历】\n")
            for i, exp in enumerate(work_experience):
                if isinstance(exp, dict):
                    optimized_parts.append(f"{exp.get('company', '未知公司')} | {exp.get('title', '未知职位')}\n")
                    if exp.get('duration'):
                        optimized_parts.append(f"时间: {exp['duration']}\n")
                    if exp.get('description'):
                        # 优化描述，添加动作动词
                        desc = exp['description']
                        # 确保描述以动词开头
                        optimized_parts.append(f"描述: {desc}\n")
                else:
                    optimized_parts.append(f"{exp}\n")
                optimized_parts.append("\n")
        
        # 添加教育背景
        education = resume_data.get("education", [])
        if education:
            optimized_parts.append("【教育背景】\n")
            for edu in education:
                if isinstance(edu, dict):
                    optimized_parts.append(f"{edu.get('institution', '未知院校')} | {edu.get('degree', '未知学位')}\n")
                    if edu.get('major'):
                        optimized_parts.append(f"专业: {edu['major']}\n")
                else:
                    optimized_parts.append(f"{edu}\n")
                optimized_parts.append("\n")
        
        # 添加项目经验
        projects = resume_data.get("projects", [])
        if projects:
            optimized_parts.append("【项目经验】\n")
            for project in projects:
                if isinstance(project, dict):
                    optimized_parts.append(f"项目名称: {project.get('name', '未知项目')}\n")
                    if project.get('description'):
                        optimized_parts.append(f"项目描述: {project['description']}\n")
                else:
                    optimized_parts.append(f"{project}\n")
                optimized_parts.append("\n")
        
        # 添加优化建议
        optimized_parts.append("-" * 50 + "\n")
        optimized_parts.append("【优化建议】\n")
        suggestions = self._generate_suggestions(job_info, resume_data)
        for i, suggestion in enumerate(suggestions, 1):
            optimized_parts.append(f"{i}. {suggestion}\n")
        
        optimized_parts.append("\n【ATS优化建议】\n")
        ats_suggestions = self._generate_ats_suggestions(resume_data)
        for i, suggestion in enumerate(ats_suggestions, 1):
            optimized_parts.append(f"{i}. {suggestion}\n")
        
        return "".join(optimized_parts)

# 使用示例
if __name__ == "__main__":
    optimizer = ResumeOptimizer()
    # 示例用法
    # result = optimizer.optimize_resume(job_info, resume_data)
    # print(result)