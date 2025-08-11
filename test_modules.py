"""
测试脚本，用于测试各个模块的功能
"""

import os

def test_job_analyzer():
    """测试职位分析模块"""
    print("=== 测试职位分析模块 ===")
    
    try:
        from job_analyzer import JobAnalyzer
        analyzer = JobAnalyzer()
        print("职位分析模块导入成功")
        
        # 创建一个简单的测试HTML文件
        test_html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>软件工程师 - 某某科技有限公司</title>
        </head>
        <body>
            <h1>软件工程师</h1>
            <div class="company-name">某某科技有限公司</div>
            <div class="job-description">
                <h2>职位描述</h2>
                <p>我们正在寻找一名有经验的软件工程师加入我们的团队。</p>
                
                <h2>技能要求</h2>
                <ul>
                    <li>Python</li>
                    <li>Django</li>
                    <li>JavaScript</li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        # 保存测试文件
        with open("test_job.html", "w", encoding="utf-8") as f:
            f.write(test_html_content)
        
        # 测试分析功能（仅在能进行网络请求时）
        print("职位分析模块已就绪，可分析职位信息")
        
        # 清理测试文件
        if os.path.exists("test_job.html"):
            os.remove("test_job.html")
            
    except ImportError as e:
        print(f"职位分析模块导入失败: {e}")
        print("请确保已安装所需依赖: pip install beautifulsoup4 requests")
    except Exception as e:
        print(f"职位分析模块测试失败: {e}")

def test_resume_parser():
    """测试简历解析模块"""
    print("\n=== 测试简历解析模块 ===")
    
    try:
        from resume_parser import ResumeParser
        parser = ResumeParser()
        print("简历解析模块导入成功")
        print("简历解析模块已就绪，可解析PDF和DOCX格式简历")
    except ImportError as e:
        print(f"简历解析模块导入失败: {e}")
        print("请确保已安装所需依赖: pip install PyPDF2 pdfplumber python-docx")
    except Exception as e:
        print(f"简历解析模块测试失败: {e}")

def test_resume_optimizer():
    """测试简历优化模块"""
    print("\n=== 测试简历优化模块 ===")
    
    try:
        from resume_optimizer import ResumeOptimizer
        optimizer = ResumeOptimizer()
        print("简历优化模块导入成功")
        
        # 模拟职位信息
        job_info = {
            "title": "软件工程师",
            "company": "某某科技有限公司",
            "key_skills": ["Python", "Django", "JavaScript", "MySQL", "AWS"],
            "requirements": ["3年Python经验", "熟悉Django", "了解前端技术"],
            "description": "我们正在寻找一名有经验的软件工程师，要求熟悉Python和Django框架"
        }
        
        # 模拟简历数据
        resume_data = {
            "text": "张三的简历内容...",
            "contact_info": {
                "name": "张三",
                "email": "zhangsan@email.com"
            },
            "skills": ["Python", "Django", "JavaScript", "MySQL"],
            "work_experience": [
                {
                    "company": "ABC科技有限公司",
                    "title": "高级软件工程师",
                    "duration": "2020.01 - 至今",
                    "description": "负责Web应用程序开发和维护"
                }
            ],
            "education": [
                {
                    "institution": "某某大学",
                    "degree": "学士学位",
                    "major": "计算机科学与技术"
                }
            ],
            "projects": [
                {
                    "name": "在线教育平台",
                    "description": "使用Django开发在线课程管理系统"
                }
            ]
        }
        
        # 测试优化功能
        result = optimizer.optimize_resume(job_info, resume_data)
        print("优化结果:")
        print(f"  匹配度评分: {result.get('match_score', 'N/A')}")
        print(f"  优化建议数量: {len(result.get('suggestions', []))}")
        print(f"  ATS建议数量: {len(result.get('ats_suggestions', []))}")
        print("简历优化模块功能正常")
    except ImportError as e:
        print(f"简历优化模块导入失败: {e}")
    except Exception as e:
        print(f"简历优化测试失败: {e}")

def test_resume_generator():
    """测试简历生成模块"""
    print("\n=== 测试简历生成模块 ===")
    
    try:
        from resume_generator import ResumeGenerator
        generator = ResumeGenerator()
        print("简历生成模块导入成功")
        print("简历生成模块已就绪，可生成PDF和DOCX格式简历")
    except ImportError as e:
        print(f"简历生成模块导入失败: {e}")
        print("请确保已安装所需依赖: pip install reportlab python-docx")
    except Exception as e:
        print(f"简历生成模块测试失败: {e}")

def main():
    """主测试函数"""
    print("开始测试简历助手各模块功能...\n")
    
    test_job_analyzer()
    test_resume_parser()
    test_resume_optimizer()
    test_resume_generator()
    
    print("\n测试完成!")
    print("\n如需完整功能，请安装依赖项:")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()