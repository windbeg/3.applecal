import subprocess
import csv
import re
from datetime import datetime

def run_applescript():
    script_path = '/Users/mac/trae/3.applecal/cal.scpt'
    try:
        # 使用 osascript 命令运行 AppleScript
        result = subprocess.run(['osascript', script_path], 
                             capture_output=True, 
                             text=True)
        
        if result.returncode == 0:
            print("日历数据导出成功！")
            return True
        else:
            print(f"错误: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"执行脚本时发生错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 步骤1：运行AppleScript导出日历数据
    print("步骤1：导出日历数据...")
    if not run_applescript():
        print("导出日历数据失败，程序终止")
        exit(1)
    
    print("数据导出完成")
    print("test")##hi