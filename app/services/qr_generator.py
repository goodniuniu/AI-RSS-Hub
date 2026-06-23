"""
二维码生成服务
为文章链接生成二维码图片，用于墨水屏显示
"""
import qrcode
import os
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


# 二维码配置
QR_CODE_SIZE = 200  # 二维码尺寸（适合墨水屏）
QR_CODE_BORDER = 4  # 二维码边框
QR_CODE_BOX_SIZE = 10  # 每个模块的像素数
STATIC_DIR = "static/qrcodes"  # 二维码存储目录


def ensure_qr_directory():
    """确保二维码存储目录存在"""
    qr_dir = os.path.join(STATIC_DIR)
    os.makedirs(qr_dir, exist_ok=True)
    return qr_dir


def generate_qr_code_url(article_id: int, article_link: str) -> str:
    """
    为文章生成二维码并返回URL

    Args:
        article_id: 文章ID
        article_link: 文章链接

    Returns:
        二维码图片URL（如：/static/qrcodes/1.png）
    """
    try:
        # 确保目录存在
        qr_dir = ensure_qr_directory()

        # 生成二维码文件名
        qr_filename = f"{article_id}.png"
        qr_path = os.path.join(qr_dir, qr_filename)

        # 如果文件已存在，直接返回URL
        if os.path.exists(qr_path):
            return f"/static/qrcodes/{qr_filename}"

        # 创建二维码（适合黑白墨水屏的高对比度设置）
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=QR_CODE_BOX_SIZE,
            border=QR_CODE_BORDER,
        )

        qr.add_data(article_link)
        qr.make(fit=True)

        # 创建二维码图片（黑白模式）
        img = qr.make_image(fill_color="black", back_color="white")

        # 保存图片
        img.save(qr_path)

        logger.info(f"生成二维码: {qr_filename} -> {article_link[:50]}...")

        return f"/static/qrcodes/{qr_filename}"

    except Exception as e:
        logger.error(f"生成二维码失败 (文章ID: {article_id}): {e}")
        return ""


def generate_qr_code_base64(article_id: int, article_link: str, size: int = 200) -> Optional[str]:
    """
    为文章生成二维码并返回Base64编码

    Args:
        article_id: 文章ID
        article_link: 文章链接
        size: 二维码尺寸

    Returns:
        Base64编码的PNG图片数据
    """
    try:
        import base64
        from io import BytesIO

        # 创建二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(article_link)
        qr.make(fit=True)

        # 创建二维码图片
        img = qr.make_image(fill_color="black", back_color="white")

        # 调整大小
        if size != 200:
            img = img.resize((size, size))

        # 转换为Base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    except Exception as e:
        logger.error(f"生成Base64二维码失败 (文章ID: {article_id}): {e}")
        return None


def delete_qr_code(article_id: int):
    """
    删除文章的二维码文件

    Args:
        article_id: 文章ID
    """
    try:
        qr_dir = ensure_qr_directory()
        qr_filename = f"{article_id}.png"
        qr_path = os.path.join(qr_dir, qr_filename)

        if os.path.exists(qr_path):
            os.remove(qr_path)
            logger.info(f"删除二维码: {qr_filename}")

    except Exception as e:
        logger.error(f"删除二维码失败 (文章ID: {article_id}): {e}")
