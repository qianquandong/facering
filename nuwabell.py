#!/usr/bin/env python3
"""
FaceRing - 智能门铃 POC
按空格拍照 → 上传 Nuwa API → 轮询结果 → Discord 推送
"""
import cv2
import os
import time
import requests
import json
from datetime import datetime
from pathlib import Path

# 配置
OUTPUT_DIR = os.path.expanduser("~/FaceRing/captures")
NUWA_API_KEY = "nw_sk_ac14334fa166699b8a2932c3cb4da0fe7dee04dd7576b3fcce5c9b4cabf8ccc5"
NUWA_API_URL = "https://gateway.nuwa.world/api/v1/face-search"
DISCORD_WEBHOOK_URL = None  # 可选：直接发到当前频道不需要 webhook，用内置消息

# Nuwa API headers
HEADERS = {
    "Authorization": f"Bearer {NUWA_API_KEY}"
}

def upload_to_nuwa(image_path):
    """上传图片到 Nuwa，返回 search_id"""
    with open(image_path, "rb") as f:
        files = {"image": f}
        response = requests.post(NUWA_API_URL, files=files, headers=HEADERS)
    
    if response.status_code == 202:
        data = response.json()
        return data.get("search_id")
    else:
        print(f"❌ 上传失败: {response.status_code} - {response.text}")
        return None

def poll_nuwa(search_id):
    """轮询 Nuwa 结果"""
    url = f"{NUWA_API_URL}/{search_id}"
    
    while True:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ 查询失败: {response.status_code}")
            return None
        
        data = response.json()
        status = data.get("status")
        
        if status == "completed":
            return data.get("results", [])
        elif status == "processing":
            print("⏳ 处理中... 等待 5 秒")
            time.sleep(5)
        else:
            print(f"❌ 未知状态: {status}")
            return None

def format_results(results):
    """格式化结果为 Discord 消息"""
    if not results:
        return "❓ 未找到匹配人脸"
    
    lines = ["**🔔 门铃响了！**\n"]
    
    for r in results[:5]:  # 只显示前 5 个
        score = r.get("score", 0)
        url = r.get("url", "")
        if score and score > 30:  # 只显示置信度 > 30% 的
            lines.append(f"**{score}%** 匹配")
            if url:
                lines.append(f"来源: {url}")
            lines.append("")
    
    return "".join(lines) if len(lines) > 1 else "❓ 未找到匹配人脸"

def send_to_discord(message, image_path=None):
    """发送到 Discord（当前频道）"""
    # 使用 OpenClaw 的 message 工具
    # 这里我们先打印结果
    print(f"\n📱 Discord 消息:\n{message}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    print("🔔 FaceRing 已启动")
    print("   按 [空格键] 拍照并查询")
    print("   按 [Q] 退出\n")
    
    window_name = "FaceRing"
    cv2.namedWindow(window_name)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(10) & 0xFF
        
        if key == ord(' '):
            # 1. 拍照
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            cv2.imwrite(filepath, frame)
            print(f"\n📷 已拍照: {filepath}")
            
            # 2. 上传 Nuwa
            print("⬆️ 上传至 Nuwa...")
            search_id = upload_to_nuwa(filepath)
            if not search_id:
                continue
            
            print(f"🔍 Search ID: {search_id}")
            print("⏳ 等待结果...")
            
            # 3. 轮询结果
            results = poll_nuwa(search_id)
            
            # 4. 发送 Discord
            message = format_results(results)
            print(f"\n{message}")
            
        elif key == ord('q'):
            print("👋 退出")
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
