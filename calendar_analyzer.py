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

def run_applescript():
    script_path = '/Users/mac/trae/3.applecal/cal.scpt'
    try:
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

def read_calendar_data(file_path):
    events = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        for i, row in enumerate(reader, 1):
            try:
                date_pattern = re.compile(
                    r'^.*?(\d{4}年\d{1,2}月\d{1,2}日)'  # 日期匹配
                    r'(?:\s*\S+\s+)?'                   # 可选星期
                    r'(\d{1,2}:\d{2}:\d{2})'            # 时间
                    r'.*$'                              # 忽略后续内容
                )
                
                def clean_date(date_str):
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
    one_month_ago = current_date.replace(day=1) - timedelta(days=1)
    three_months_ago = current_date - relativedelta(months=3)
    twelve_months_ago = current_date.replace(year=current_date.year - 1)

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
            
            if start >= one_month_ago:
                date_key = start.strftime("%Y-%m-%d")
                update_stat(stats['daily'][date_key], category, event_name, duration)
            
            if start >= three_months_ago:
                week_key = f"{start.year}-W{start.isocalendar()[1]:02d}"
                update_stat(stats['weekly'][week_key], category, event_name, duration)
            
            if start >= twelve_months_ago:
                month_key = f"{start.year}-{start.month:02d}"
                update_stat(stats['monthly'][month_key], category, event_name, duration)
                stats['category_summary'][category] += duration

        except KeyError as e:
            print(f"事件解析失败 - 缺少字段 {e}")
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
    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"服务器启动在 http://localhost:{PORT}")
        webbrowser.open(f"http://localhost:{PORT}")
        httpd.serve_forever()

def main():
    # 步骤1：运行AppleScript导出日历数据
    print("步骤1：导出日历数据...")
    if not run_applescript():
        print("导出日历数据失败，程序终止")
        return
    
    # 步骤2：处理数据并生成JSON
    print("\n步骤2：分析日历数据...")
    file_path = './calendar_export.csv'
    events = read_calendar_data(file_path)
    stats = analyze_events(events)
    
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