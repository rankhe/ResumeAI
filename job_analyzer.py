"""
职位分析模块
负责从URL抓取职位信息并提取关键要求
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, List
from urllib.parse import urlparse

class JobAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 定义不同网站的选择器规则
        self.site_selectors = {
            'linkedin': {
                'title': 'h1.topcard__title',
                'company': 'a.topcard__org-name-link',
                'description': '.show-more-less-html__markup',
                'location': 'span.topcard__flavor:nth-child(2)'
            },
            'zhaopin': {  # 智联招聘
                'title': 'h1::text',
                'company': '.company-name',
                'description': '.job-detail-body',
                'location': '.job-address'
            },
            '51job': {  # 前程无忧
                'title': 'h1',
                'company': '.company-name',
                'description': '.job-detail',
                'location': '.job-location'
            },
            'default': {
                'title': 'h1, [class*="title"], [data-testid="job-title"], title',
                'company': '[class*="company"], [data-testid="company-name"], [class*="employer"]',
                'description': '[class*="description"], [data-testid="job-description"], [class*="job-desc"]',
                'location': '[class*="location"], [class*="address"]'
            }
        }
    
    def analyze_job_posting(self, url: str) -> Dict:
        """
        分析职位描述页面，提取关键信息
        
        Args:
            url: 职位页面URL
            
        Returns:
            包含职位信息的字典
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 根据URL识别网站类型
            site_type = self._identify_site(url)
            selectors = self.site_selectors.get(site_type, self.site_selectors['default'])
            
            # 提取职位信息
            job_info = {
                "url": url,
                "title": self._extract_by_selectors(soup, selectors.get('title', '')),
                "company": self._extract_by_selectors(soup, selectors.get('company', '')),
                "description": self._extract_by_selectors(soup, selectors.get('description', '')),
                "location": self._extract_by_selectors(soup, selectors.get('location', '')),
                "requirements": self._extract_requirements(soup),
                "key_skills": self._extract_key_skills(soup)
            }
            
            return job_info
        except Exception as e:
            raise Exception(f"职位分析失败: {str(e)}")
    
    def _identify_site(self, url: str) -> str:
        """
        根据URL识别招聘网站类型
        
        Args:
            url: 职位页面URL
            
        Returns:
            网站类型标识
        """
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname.lower() if parsed_url.hostname else ''
        
        if 'linkedin.com' in hostname:
            return 'linkedin'
        elif 'zhaopin.com' in hostname:
            return 'zhaopin'
        elif '51job.com' in hostname:
            return '51job'
        else:
            return 'default'
    
    def _extract_by_selectors(self, soup: BeautifulSoup, selectors_str: str) -> str:
        """
        根据选择器字符串提取内容
        
        Args:
            soup: BeautifulSoup对象
            selectors_str: 选择器字符串，用逗号分隔多个选择器
            
        Returns:
            提取的内容
        """
        if not selectors_str:
            return ""
            
        selectors = [s.strip() for s in selectors_str.split(',')]
        
        for selector in selectors:
            # 处理::text伪选择器
            if '::text' in selector:
                css_selector = selector.replace('::text', '').strip()
                elements = soup.select(css_selector)
                if elements:
                    # 尝试获取直接文本内容
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text:
                            return text
            else:
                # 标准CSS选择器
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text:
                        return text
        
        return ""
    
    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """
        提取职位标题
        """
        # 使用通用方法
        return self._extract_by_selectors(soup, 'h1, [class*="title"], [data-testid="job-title"], title')

    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """
        提取公司名称
        """
        # 使用通用方法
        return self._extract_by_selectors(soup, '[class*="company"], [data-testid="company-name"], [class*="employer"]')
    
    def _extract_job_description(self, soup: BeautifulSoup) -> str:
        """
        提取职位描述
        """
        # 使用通用方法
        return self._extract_by_selectors(soup, '[class*="description"], [data-testid="job-description"], [class*="job-desc"]')
    
    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        """
        提取职位要求
        """
        # 查找包含"要求"、"需求"、"requirement"等关键词的元素
        requirement_keywords = ['要求', '需求', 'requirement', 'qualification', '资格', 'responsibilit', '职责']
        requirements = []
        
        for keyword in requirement_keywords:
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                parent = element.parent
                # 查找列表项或段落
                siblings = parent.find_next_siblings()
                for sibling in siblings:
                    if sibling.name in ['li', 'p', 'div']:
                        text = sibling.get_text().strip()
                        if text and len(text) > 5:  # 过滤太短的内容
                            requirements.append(text)
                            break  # 找到一个就够了，避免重复
                
                # 如果在siblings中没找到，尝试在parent的子元素中查找
                if not requirements:
                    children = parent.find_all(['li', 'p', 'div'])
                    for child in children:
                        text = child.get_text().strip()
                        if text and len(text) > 5:
                            requirements.append(text)
                            break
        
        # 如果通过关键词没找到，尝试查找包含"要求"的section
        if not requirements:
            requirement_sections = soup.find_all(string=re.compile(r'(要求|requirement|资格)', re.IGNORECASE))
            for section in requirement_sections:
                parent = section.parent
                # 查找兄弟元素中的列表
                next_elem = parent.find_next()
                while next_elem and len(requirements) < 10:  # 限制数量
                    if next_elem.name == 'ul':
                        for li in next_elem.find_all('li'):
                            text = li.get_text().strip()
                            if text and len(text) > 5:
                                requirements.append(text)
                    elif next_elem.name == 'li':
                        text = next_elem.get_text().strip()
                        if text and len(text) > 5:
                            requirements.append(text)
                    next_elem = next_elem.find_next()
        
        return requirements if requirements else ["未明确列出具体要求"]
    
    def _extract_key_skills(self, soup: BeautifulSoup) -> List[str]:
        """
        提取关键技能
        """
        # 常见技能关键词
        tech_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Vue', 'Angular',
            'Node.js', 'Express', 'Django', 'Flask', 'Spring',
            'SQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'AWS', 'Docker', 'Kubernetes', 'Git',
            'Machine Learning', 'AI', '数据分析', '云计算',
            'TensorFlow', 'PyTorch', 'Hadoop', 'Spark',
            'Linux', 'Windows', 'macOS', 'CI/CD',
            'DevOps', 'Agile', 'Scrum', 'JIRA'
        ]
        
        job_text = soup.get_text()
        found_skills = []
        
        for skill in tech_skills:
            # 使用正则表达式进行更灵活的匹配
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, job_text, re.IGNORECASE):
                found_skills.append(skill)
        
        return found_skills

# 使用示例
if __name__ == "__main__":
    analyzer = JobAnalyzer()
    # 示例URL，实际使用时需要替换为真实的职位页面URL
    # job_info = analyzer.analyze_job_posting("https://example-job-site.com/job/12345")
    # print(job_info)