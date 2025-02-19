import csv
import re
from datetime import datetime, timedelta
from collections import defaultdict
import json
from dateutil.relativedelta import relativedelta


def read_calendar_data(file_path):
    events = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='|')
        for i, row in enumerate(reader, 1):
            try:
                # Handle empty/invalid dates first
                # Clean and validate date strings
                date_pattern = re.compile(
                    r'^.*?(\d{4}年\d{1,2}月\d{1,2}日)'  # 日期匹配
                    r'(?:\s*\S+\s+)?'                   # 可选星期
                    r'(\d{1,2}:\d{2}:\d{2})'            # 时间
                    r'.*$'                              # 忽略后续内容
                )
                
                def clean_date(date_str):
                    """Extract date/time parts from messy strings"""
                    match = date_pattern.search(date_str)
                    if not match:
                        raise ValueError(f"No date pattern found in: {date_str}")
                    return f"{match.group(1)} {match.group(2)}"
                
                # Clean both start and end dates
                cleaned_start = clean_date(row['Start Date'])
                cleaned_end = clean_date(row['End Date'])
                
                # Use single format after cleaning
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
    """分析日历事件并生成结构化统计数据"""
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

    # 获取当前时间
    current_date = datetime.now()
    
    # 计算时间范围
    one_month_ago = current_date.replace(day=1) - timedelta(days=1)
    three_months_ago = current_date - relativedelta(months=3)
    twelve_months_ago = current_date.replace(year=current_date.year - 1)

    for event in events:
        try:
            # 计算持续时间（小时）
            duration = (event['end_date'] - event['start_date']).total_seconds() / 3600
            
            # 获取时间维度键
            start = event['start_date']
            
            # 仅处理在时间范围内的数据
            if start >= one_month_ago:
                date_key = start.strftime("%Y-%m-%d")
                update_stat(stats['daily'][date_key], category, event_name, duration)
            
            if start >= three_months_ago:
                week_key = f"{start.year}-W{start.isocalendar()[1]:02d}"
                update_stat(stats['weekly'][week_key], category, event_name, duration)
            
            if start >= twelve_months_ago:
                month_key = f"{start.year}-{start.month:02d}"
                update_stat(stats['monthly'][month_key], category, event_name, duration)
            
            # 分类逻辑（根据日历名称判断）
            category = '个人' if '个人' in event['calendar'] else '工作'
            event_name = event.get('summary', '未命名事件').strip()
            
            # 更新总分类统计（只统计最近12个月的数据）
            if start >= twelve_months_ago:
                stats['category_summary'][category] += duration

        except KeyError as e:
            print(f"事件解析失败 - 缺少字段 {e}")
        except Exception as e:
            print(f"处理事件时发生错误: {str(e)}")

    # 计算百分比
    calculate_percentages(stats)
    return stats

def update_stat(period_stat, category, event_name, duration):
    """更新时间段统计"""
    period_stat['total'] += duration
    period_stat['categories'][category] += duration
    period_stat.setdefault('events', defaultdict(float))[event_name] += duration

def calculate_percentages(stats):
    """计算各类别时间占比"""
    total_hours = sum(stats['category_summary'].values())
    
    if total_hours > 0:
        for category in stats['category_summary']:
            stats['category_summary'][category] = {
                'hours': stats['category_summary'][category],
                'percentage': stats['category_summary'][category] / total_hours * 100
            }

    return stats

if __name__ == "__main__":
    file_path = './calendar_export.csv'
    events = read_calendar_data(file_path)
    stats = analyze_events(events)
    
    # 输出格式化JSON
    with open('./calendar_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(
            {
                'daily': stats['daily'],
                'weekly': stats['weekly'],
                'monthly': stats['monthly'],
                'category_summary': stats['category_summary']
            }, 
            f,
            ensure_ascii=False,  # 支持中文显示
            indent=2,  # 添加缩进
            default=lambda o: dict(o) if isinstance(o, defaultdict) else o
        )
