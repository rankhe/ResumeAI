import json
import os
from typing import Dict, List, Optional

class TemplateManager:
    """模板管理器，负责管理和操作简历模板"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        初始化模板管理器
        
        Args:
            templates_dir: 模板文件夹路径
        """
        self.templates_dir = templates_dir
        self._ensure_templates_dir()
    
    def _ensure_templates_dir(self):
        """确保模板目录存在"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def get_available_templates(self) -> List[Dict]:
        """
        获取所有可用的模板
        
        Returns:
            模板列表，每个模板包含基本信息
        """
        templates = []
        
        if not os.path.exists(self.templates_dir):
            return templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                    
                    # 提取模板基本信息
                    template_info = {
                        "id": filename.replace('.json', ''),
                        "title": template_data.get("title", "未知职位"),
                        "company": template_data.get("company", "未知公司"),
                        "description": template_data.get("description", "")[:100] + "..." if len(template_data.get("description", "")) > 100 else template_data.get("description", ""),
                        "skills_count": len(template_data.get("key_skills", [])),
                        "requirements_count": len(template_data.get("requirements", []))
                    }
                    templates.append(template_info)
                except Exception as e:
                    print(f"读取模板文件 {filename} 失败: {str(e)}")
                    continue
        
        return templates
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict]:
        """
        根据ID获取模板详细信息
        
        Args:
            template_id: 模板ID
            
        Returns:
            模板详细信息，如果不存在返回None
        """
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        
        if not os.path.exists(template_path):
            return None
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取模板 {template_id} 失败: {str(e)}")
            return None
    
    def create_template(self, template_data: Dict, template_id: str) -> bool:
        """
        创建新模板
        
        Args:
            template_data: 模板数据
            template_id: 模板ID
            
        Returns:
            是否创建成功
        """
        try:
            template_path = os.path.join(self.templates_dir, f"{template_id}.json")
            
            # 验证模板数据结构
            required_fields = ["title", "company", "description", "requirements", "key_skills"]
            for field in required_fields:
                if field not in template_data:
                    raise ValueError(f"模板缺少必需字段: {field}")
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"创建模板失败: {str(e)}")
            return False
    
    def update_template(self, template_id: str, template_data: Dict) -> bool:
        """
        更新现有模板
        
        Args:
            template_id: 模板ID
            template_data: 新的模板数据
            
        Returns:
            是否更新成功
        """
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        
        if not os.path.exists(template_path):
            return False
        
        try:
            # 验证模板数据结构
            required_fields = ["title", "company", "description", "requirements", "key_skills"]
            for field in required_fields:
                if field not in template_data:
                    raise ValueError(f"模板缺少必需字段: {field}")
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"更新模板失败: {str(e)}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """
        删除模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            是否删除成功
        """
        template_path = os.path.join(self.templates_dir, f"{template_id}.json")
        
        if not os.path.exists(template_path):
            return False
        
        try:
            os.remove(template_path)
            return True
        except Exception as e:
            print(f"删除模板失败: {str(e)}")
            return False
    
    def search_templates(self, keyword: str) -> List[Dict]:
        """
        搜索模板
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的模板列表
        """
        all_templates = self.get_available_templates()
        matching_templates = []
        
        keyword_lower = keyword.lower()
        
        for template in all_templates:
            # 在标题、公司名、描述中搜索关键词
            if (keyword_lower in template["title"].lower() or 
                keyword_lower in template["company"].lower() or 
                keyword_lower in template["description"].lower()):
                matching_templates.append(template)
        
        return matching_templates
    
    def get_template_categories(self) -> Dict[str, List[str]]:
        """
        获取模板分类
        
        Returns:
            按类别分组的模板ID列表
        """
        categories = {
            "技术类": [],
            "数据类": [],
            "管理类": [],
            "设计类": [],
            "其他": []
        }
        
        templates = self.get_available_templates()
        
        for template in templates:
            title = template["title"].lower()
            template_id = template["id"]
            
            if any(keyword in title for keyword in ["工程师", "开发", "程序员", "技术"]):
                categories["技术类"].append(template_id)
            elif any(keyword in title for keyword in ["数据", "分析师", "算法"]):
                categories["数据类"].append(template_id)
            elif any(keyword in title for keyword in ["经理", "主管", "总监", "管理"]):
                categories["管理类"].append(template_id)
            elif any(keyword in title for keyword in ["设计师", "UI", "UX", "美工"]):
                categories["设计类"].append(template_id)
            else:
                categories["其他"].append(template_id)
        
        return categories

# 使用示例
if __name__ == "__main__":
    manager = TemplateManager()
    
    # 获取所有模板
    templates = manager.get_available_templates()
    print("可用模板:")
    for template in templates:
        print(f"- {template['title']} ({template['company']})")
    
    # 获取特定模板
    template = manager.get_template_by_id("software_engineer")
    if template:
        print(f"\n软件工程师模板: {template['title']}")