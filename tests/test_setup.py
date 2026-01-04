#!/usr/bin/env python3
"""
AI-RSS-Hub 环境测试脚本
用于验证依赖安装和配置是否正确
"""

import sys
import os


def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.10 或以上")
        return False


def check_dependencies():
    """检查依赖包"""
    print("\n🔍 检查依赖包...")
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("sqlmodel", "SQLModel"),
        ("feedparser", "feedparser"),
        ("openai", "OpenAI"),
        ("apscheduler", "APScheduler"),
    ]

    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} 未安装")
            all_ok = False

    return all_ok


def check_env_file():
    """检查 .env 文件"""
    print("\n🔍 检查环境变量配置...")
    if not os.path.exists(".env"):
        print("❌ .env 文件不存在")
        print("   请执行：cp .env.example .env")
        return False

    print("✅ .env 文件存在")

    # 读取并检查关键配置
    with open(".env", "r") as f:
        content = f.read()

    if "OPENAI_API_KEY=your_api_key_here" in content or "OPENAI_API_KEY=sk-your" in content:
        print("⚠️  警告：API Key 未配置（仍为示例值）")
        return False
    elif "OPENAI_API_KEY=sk-" in content:
        print("✅ OPENAI_API_KEY 已配置")
        return True
    else:
        print("⚠️  警告：未找到 OPENAI_API_KEY")
        return False


def test_database_connection():
    """测试数据库连接"""
    print("\n🔍 测试数据库连接...")
    try:
        from app.database import create_db_and_tables, engine
        from sqlmodel import Session

        create_db_and_tables()
        with Session(engine) as session:
            # 简单测试
            pass
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_llm_api():
    """测试 LLM API 连接"""
    print("\n🔍 测试 LLM API 连接...")
    try:
        from app.services.summarizer import test_llm_connection

        if test_llm_connection():
            print("✅ LLM API 连接成功")
            return True
        else:
            print("❌ LLM API 连接失败")
            print("   请检查 .env 中的 OPENAI_API_KEY 和 OPENAI_API_BASE")
            return False
    except Exception as e:
        print(f"❌ LLM API 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 50)
    print("  AI-RSS-Hub 环境测试")
    print("=" * 50)

    results = {
        "Python 版本": check_python_version(),
        "依赖包": check_dependencies(),
        "环境变量": check_env_file(),
    }

    # 只有前面都成功才测试数据库和 API
    if all(results.values()):
        results["数据库"] = test_database_connection()
        results["LLM API"] = test_llm_api()

    print("\n" + "=" * 50)
    print("  测试结果汇总")
    print("=" * 50)

    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")

    print("=" * 50)

    if all(results.values()):
        print("\n🎉 所有测试通过！可以启动应用了")
        print("\n启动命令：")
        print("  ./start.sh")
        print("  或")
        print("  python -m uvicorn app.main:app --reload")
        return 0
    else:
        print("\n⚠️  部分测试失败，请按照提示修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())
