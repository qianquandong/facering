#!/usr/bin/env python3
"""
FaceRing POC - 摄像头测试
"""
import cv2
import os
from datetime import datetime

OUTPUT_DIR = os.path.expanduser("~/FaceRing/captures")

def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 打开摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return
    
    print("📷 FaceRing - 按空格拍照")
    print("   按 [空格键] 拍照")
    print("   按 [Q] 退出")
    print()
    
    # 显示实时预览窗口
    window_name = "FaceRing"
    cv2.namedWindow(window_name)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ 无法读取摄像头画面")
            break
        
        # 显示画面
        cv2.imshow(window_name, frame)
        
        # 等待按键 (10ms)
        key = cv2.waitKey(10) & 0xFF
        
        if key == ord(' '):  # 空格键
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.jpg"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 保存图片
            cv2.imwrite(filepath, frame)
            print(f"✅ 已保存: {filepath}")
            
        elif key == ord('q'):  # Q 退出
            print("👋 退出")
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
