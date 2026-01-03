#!/usr/bin/env python3
"""
生成安全的 API Token

用于 AI-RSS-Hub 的 API 认证
"""
import secrets
import sys


def generate_token(length: int = 32) -> str:
    """
    生成安全的随机 Token

    Args:
        length: Token 字节长度（默认 32）

    Returns:
        URL 安全的 base64 编码 Token
    """
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    # 生成 Token
    token = generate_token()

    # 输出结果
    print("=" * 60)
    print("生成的 API Token:")
    print("=" * 60)
    print(token)
    print("=" * 60)
    print()
    print("请将此 Token 添加到 .env 文件:")
    print(f"API_TOKEN={token}")
    print()
    print("⚠️  请妥善保管此 Token，不要泄露到版本控制系统")
    print()
    print("使用示例:")
    print(f'curl -H "X-API-Token: {token}" http://localhost:8000/api/feeds')
