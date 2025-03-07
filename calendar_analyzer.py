import subprocess
import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict
import json
from dateutil.relativedelta import relativedelta
import http.server
import socketserver
import os
import webbrowser
import pathlib

def run_applescript(start_date=None):
    script_path = './cal.scpt'
    try:
        cmd = ['osascript', script_path]
        if start_date:
            # 将日期转换为AppleScript可接受的格式
            date_str = start_date.strftime('%Y-%m-%d')
            cmd.extend([date_str])
            print(f'导出日历起始日期：{date_str}')
            
        result = subprocess.run(cmd, 
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

def read_calendar_data(file_path):
    events = []
    
    # 检查文件是否存在，如果不存在则返回空列表
    if not os.path.exists(file_path):
        return events
        
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        for i, row in enumerate(reader, 1):
            try:
                date_pattern = re.compile(
                    r'(\d{4}年\d{1,2}月\d{1,2}日)(?:\s+星期[一二三四五六日])?\s+(\d{1,2}:\d{2}:\d{2})'  # 日期和时间匹配
                )
                
                def clean_date(date_str):
                    # 如果日期字符串包含分隔符"-"，只取第一部分
                    if ' - ' in date_str:
                        date_str = date_str.split(' - ')[0]
                    
                    match = date_pattern.search(date_str)
                    if not match:
                        raise ValueError(f"No date pattern found in: {date_str}")
                    return f"{match.group(1)} {match.group(2)}"
                
                cleaned_start = clean_date(row['Start Date'])
                cleaned_end = clean_date(row['End Date'])
                
                date_format = '%Y年%m月%d日 %H:%M:%S'
                
                try:
                    start_date = datetime.strptime(cleaned_start, date_format)
                    end_date = datetime.strptime(cleaned_end, date_format)
                except ValueError as e:
                    raise ValueError(f"Date parsing failed: {str(e)}") from e
                
                if not start_date or not end_date:
                    raise ValueError("No valid date format found")
                
                events.append({
                    'calendar': row['Calendar'],
                    'summary': row['Summary'],
                    'start_date': start_date,
                    'end_date': end_date
                })
                
            except Exception as e:
                print(
                    f"Skipping row {i}: {str(e)} - "
                    f"{row['Start Date']} | {row['End Date']}"
                )
    return events

def analyze_events(events):
    stats = {
        'daily': defaultdict(lambda: {
            'total': 0, 
            'categories': defaultdict(float),
            'events': defaultdict(float)
        }),
        'weekly': defaultdict(lambda: {
            'total': 0,
            'categories': defaultdict(float),
            'events': defaultdict(float)
        }),
        'monthly': defaultdict(lambda: {
            'total': 0,
            'categories': defaultdict(float),
            'events': defaultdict(float)
        }),
        'category_summary': defaultdict(float)
    }

    current_date = datetime.now()
    seven_days_ago = current_date - timedelta(days=7)
    six_weeks_ago = current_date - timedelta(weeks=6)
    six_months_ago = current_date - relativedelta(months=6)

    for event in events:
        try:
            duration = (event['end_date'] - event['start_date']).total_seconds() / 3600
            start = event['start_date']
            
            # 分类逻辑（根据日历名称判断）
            if '个人' in event['calendar']:
                category = '个人'
            elif '放松' in event['calendar']:
                category = '放松'
            elif '读书' in event['calendar']:
                category = '读书'
            else:
                category = '工作'
            event_name = event.get('summary', '未命名事件').strip()
            
            if start >= seven_days_ago:
                date_key = start.strftime("%Y-%m-%d")
                update_stat(stats['daily'][date_key], category, event_name, duration)
            
            if start >= six_weeks_ago:
                week_key = f"{start.year}-W{start.isocalendar()[1]:02d}"
                update_stat(stats['weekly'][week_key], category, event_name, duration)
            
            if start >= six_months_ago:
                month_key = f"{start.year}-{start.month:02d}"
                update_stat(stats['monthly'][month_key], category, event_name, duration)
                stats['category_summary'][category] += duration

        except Exception as e:
            print(f"处理事件时发生错误: {str(e)}")

    calculate_percentages(stats)
    return stats

def update_stat(period_stat, category, event_name, duration):
    period_stat['total'] += duration
    period_stat['categories'][category] += duration
    period_stat.setdefault('events', defaultdict(float))[event_name] += duration

def calculate_percentages(stats):
    total_hours = sum(stats['category_summary'].values())
    
    if total_hours > 0:
        for category in stats['category_summary']:
            stats['category_summary'][category] = {
                'hours': stats['category_summary'][category],
                'percentage': stats['category_summary'][category] / total_hours * 100
            }

    return stats

def start_web_server():
    from web_server import start_web_server
    start_web_server()

def get_config():
    """获取配置信息，如果配置文件不存在则创建默认配置"""
    config_path = './config.json'
    config = {}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"读取配置文件失败: {str(e)}，将使用默认配置")
    
    current_date = datetime.now()
    
    # 如果没有last_run_date或配置文件不存在，设置为360天前
    if 'last_run_date' not in config:
        config['last_run_date'] = (current_date - timedelta(days=360)).strftime('%Y-%m-%d')
    
    # 解析last_run_date为datetime对象
    last_run_date = datetime.strptime(config['last_run_date'], '%Y-%m-%d')
    
    # 更新配置文件，记录本次运行时间
    config['last_run_date'] = current_date.strftime('%Y-%m-%d')
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    return last_run_date

def merge_calendar_data(new_data_path, existing_data_path):
    """合并新旧日历数据，并去除重复项"""
    # 修正日志输出，使其更清晰
    print(f'新数据路径:{new_data_path}, 现有数据路径:{existing_data_path}')
    
    # 读取新数据
    new_events = read_calendar_data(new_data_path)
    
    # 读取现有数据（如果存在）
    existing_events = read_calendar_data(existing_data_path) if os.path.exists(existing_data_path) else []
    #print(f'existing_events:{existing_events}')

    # 创建一个集合来跟踪已经存在的事件（使用事件的唯一标识）
    existing_event_keys = set()
    merged_events = []
    
    # 处理现有事件
    for event in existing_events:
        # 创建事件的唯一标识（日历+摘要+开始时间+结束时间）
        event_key = (event['calendar'], event['summary'], 
                    event['start_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    event['end_date'].strftime('%Y-%m-%d %H:%M:%S'))
        
        if event_key not in existing_event_keys:
            existing_event_keys.add(event_key)
            merged_events.append(event)
    
    # 添加新事件（如果不重复）
    new_added_events = []
    for event in new_events:
        event_key = (event['calendar'], event['summary'], 
                    event['start_date'].strftime('%Y-%m-%d %H:%M:%S'),
                    event['end_date'].strftime('%Y-%m-%d %H:%M:%S'))
        
        if event_key not in existing_event_keys:
            existing_event_keys.add(event_key)
            merged_events.append(event)
            new_added_events.append(event)  # 记录新添加的事件
    
    # 将新添加的事件写入CSV文件（追加模式）
    file_exists = os.path.exists(existing_data_path)
    print(f'保存文件:{existing_data_path}')
    with open(existing_data_path, 'a', encoding='utf-8') as f:
        if not file_exists:
            f.write("Calendar|Summary|Start Date|End Date\n")
        for event in new_added_events:  # 只写入新添加的事件
            calendar_name = event['calendar']
            summary = event['summary'].replace('"', '\\"')  # 转义双引号
            start_date = event['start_date'].strftime('%Y年%m月%d日 %H:%M:%S')
            end_date = event['end_date'].strftime('%Y年%m月%d日 %H:%M:%S')
            f.write(f"{calendar_name}|{summary}|{start_date}|{end_date}\n")
    #print(f'merge函数返回值打印：{merged_events}')
    return merged_events

def main():
    # 获取配置信息
    last_run_date = get_config()
    print(f"上次运行时间: {last_run_date.strftime('%Y-%m-%d')}")
    
    # 步骤1：运行AppleScript导出日历数据（仅获取上次运行至今的数据）
    print("步骤1：导出增量日历数据...")
    temp_csv_path = './calendar_export_temp.csv'
    
    # 备份当前的导出文件路径
    original_export_path = './calendar_export.csv'
    
    # 确保临时文件不存在
    if os.path.exists(temp_csv_path):
        os.remove(temp_csv_path)
    
    # 重命名当前的导出文件，以便AppleScript可以创建新文件
    if os.path.exists(original_export_path):
        pathlib.Path(original_export_path).rename(temp_csv_path)
    else:
        print(f"当前文件不存在: {original_export_path}，将创建该空文件")
        pathlib.Path(temp_csv_path).touch()  
    
    # 运行AppleScript获取增量数据
    if not run_applescript(last_run_date):
        print("导出日历数据失败，程序终止")
        # 恢复原始文件
        if os.path.exists(temp_csv_path):
            pathlib.Path(temp_csv_path).rename(original_export_path)
        return
    
    # 合并新旧数据并去重
    print("合并日历数据并去除重复项...")
    merged_events = merge_calendar_data(original_export_path,temp_csv_path) #两个文件顺序错了，进行了调整
    
    # 删除临时文件
    if os.path.exists(temp_csv_path):
        if os.path.exists(original_export_path):
            os.remove(original_export_path)
            print(f"删除临时文件: {original_export_path}")
        pathlib.Path(temp_csv_path).rename(original_export_path)
  
    
    # 步骤2：处理数据并生成JSON
    print("\n步骤2：分析日历数据...")
    stats = analyze_events(merged_events)
    
    with open('./calendar_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(
            {
                'daily': stats['daily'],
                'weekly': stats['weekly'],
                'monthly': stats['monthly'],
                'category_summary': stats['category_summary']
            }, 
            f,
            ensure_ascii=False,
            indent=2,
            default=lambda o: dict(o) if isinstance(o, defaultdict) else o
        )
    print("数据分析完成，已生成JSON文件")
    
    # 步骤3：启动Web服务器
    print("\n步骤3：启动Web服务器...")
    start_web_server()

if __name__ == "__main__":
    main()