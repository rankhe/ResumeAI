"""
启动简历助手服务器的脚本
"""
import os
import sys

def main():
    print("=== 简历助手服务器启动脚本 ===")
    print()
    
    # 检查必要文件
    required_files = [
        "main.py",
        "frontend/index.html",
        "frontend/src/script.js",
        "frontend/src/style.css"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print()
        print("请确保所有文件都存在后再次运行。")
        return
    
    print("✅ 所有必要文件检查通过")
    print()
    
    # 启动服务器
    print("🚀 启动服务器...")
    print("📱 访问地址: http://localhost:8000")
    print("🛑 按 Ctrl+C 停止服务器")
    print()
    
    try:
        import uvicorn
        # 使用字符串导入方式，避免 reload 警告
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()