import os
import signal
import subprocess

def stop_web_server(port=8080):
    try:
        # 使用 sudo 来获取更高权限，同时使用多种方式查找进程
        cmd = f"sudo lsof -i :{port} | grep LISTEN | awk '{{print $2}}'"
        pid = subprocess.check_output(cmd, shell=True).decode().strip()
        
        if pid:
            # 使用 sudo 发送终止信号
            subprocess.run(['sudo', 'kill', '-9', pid])
            print(f"已停止运行在端口 {port} 的服务器")
        else:
            # 尝试使用 netstat 作为备选方案
            cmd = f"sudo netstat -vanp tcp | grep {port}"
            result = subprocess.check_output(cmd, shell=True).decode().strip()
            if result:
                pid = result.split()[8].split('/')[0]
                subprocess.run(['sudo', 'kill', '-9', pid])
                print(f"已停止运行在端口 {port} 的服务器")
            else:
                print(f"没有找到运行在端口 {port} 的服务器")
            
    except subprocess.CalledProcessError:
        print(f"端口 {port} 上没有运行的服务器")
    except ProcessLookupError:
        print(f"无法终止进程，可能服务器已经停止")
    except Exception as e:
        print(f"停止服务器时发生错误: {str(e)}")

if __name__ == "__main__":
    stop_web_server()