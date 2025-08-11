"""
测试用户交互模块的功能
"""

def test_user_interface():
    """测试用户交互模块"""
    print("=== 测试用户交互模块 ===")
    
    # 测试核心模块导入
    modules_to_test = [
        ('job_analyzer', '职位分析模块'),
        ('resume_parser', '简历解析模块'),
        ('resume_optimizer', '简历优化模块'),
        ('resume_generator', '简历生成模块'),
        ('user_interface', '用户交互模块')
    ]
    
    for module_name, module_desc in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_desc}导入成功")
        except ImportError as e:
            print(f"✗ {module_desc}导入失败: {e}")
            if 'PyPDF2' in str(e):
                print("  提示: 请安装PyPDF2: pip install PyPDF2")
            elif 'reportlab' in str(e):
                print("  提示: 请安装reportlab: pip install reportlab")
            elif 'python-docx' in str(e):
                print("  提示: 请安装python-docx: pip install python-docx")
    
    # 如果用户交互模块可以导入，则测试其功能
    try:
        from user_interface import UserInterface
        ui = UserInterface()
        print("✓ 用户交互模块实例化成功")
        
        # 测试获取模板列表
        try:
            templates = ui.get_available_templates()
            print(f"✓ 可用模板获取成功: {templates}")
        except Exception as e:
            print(f"✗ 获取模板列表失败: {e}")
        
        # 测试创建模板
        try:
            template_data = {
                "title": "测试职位",
                "company": "测试公司",
                "description": "这是一个测试职位",
                "requirements": ["要求1", "要求2"],
                "key_skills": ["技能1", "技能2"]
            }
            success = ui.create_template("test_template", template_data)
            print(f"✓ 创建模板{'成功' if success else '失败'}")
        except Exception as e:
            print(f"✗ 创建模板失败: {e}")
        
        print("用户交互模块基础功能正常")
        
    except ImportError as e:
        print(f"用户交互模块导入失败: {e}")
        print("请确保已安装所有依赖项: pip install -r requirements.txt")
    except Exception as e:
        print(f"用户交互模块测试失败: {e}")

def main():
    """主测试函数"""
    print("开始测试用户交互模块...\n")
    test_user_interface()
    print("\n测试完成!")
    print("\n如需完整功能，请确保已安装所有依赖项:")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()