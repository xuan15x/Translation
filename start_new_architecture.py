"""
翻译平台启动脚本 - 基于新架构
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    try:
        # 导入 GUI 应用
        from presentation.gui_app import run_gui_app
        
        # 启动 GUI
        print("🚀 启动翻译平台...")
        print("="*50)
        print("基于全新的分层架构:")
        print("  - Domain Layer (领域层)")
        print("  - Application Layer (应用层)")
        print("  - Service Layer (服务层)")
        print("  - Data Access Layer (数据访问层)")
        print("  - Infrastructure Layer (基础设施层)")
        print("="*50)
        
        run_gui_app()
        
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")


if __name__ == "__main__":
    main()
