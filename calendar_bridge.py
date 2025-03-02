from Foundation import NSDate, NSCalendar, NSCalendarUnitYear, NSDateComponents
from CalendarStore import CalCalendarStore, CalEvent, CalCalendar
from datetime import datetime, timedelta

class CalendarBridge:
    def __init__(self):
        try:
            self.store = CalCalendarStore.defaultCalendarStore()
            if self.store is None:
                raise RuntimeError("无法初始化日历存储，请检查日历访问权限")
        except Exception as e:
            raise RuntimeError(f"初始化日历存储失败: {str(e)}\n请确保已安装pyobjc-framework-CalendarStore并授予日历访问权限。")
        
    def get_calendar_by_name(self, name):
        calendars = self.store.calendars()
        for calendar in calendars:
            if calendar.title() == name:
                return calendar
        return None
    
    def get_events(self, calendar_names):
        events = []
        current_date = NSDate.date()
        
        # 计算一年前的日期
        calendar = NSCalendar.currentCalendar()
        components = NSDateComponents.alloc().init()
        components.setYear_(-1)
        one_year_ago = calendar.dateByAddingComponents_toDate_options_(components, current_date, 0)
        
        for name in calendar_names:
            cal = self.get_calendar_by_name(name)
            if cal:
                # 获取日历中的事件
                cal_events = self.store.eventsFromDate_toDate_calendars_(
                    one_year_ago,
                    current_date,
                    [cal]
                )
                
                for event in cal_events:
                    events.append({
                        'calendar': name,
                        'summary': event.title(),
                        'start_date': datetime.fromtimestamp(event.startDate().timeIntervalSince1970()),
                        'end_date': datetime.fromtimestamp(event.endDate().timeIntervalSince1970())
                    })
        
        return events

def get_calendar_events():
    bridge = CalendarBridge()
    calendar_names = ['个人', '日历', '工作', '读书']
    events = bridge.get_events(calendar_names)
    
    # 转换事件数据为CSV格式
    output = 'Calendar|Summary|Start Date|End Date\n'
    for event in events:
        calendar_name = '放松' if event['calendar'] == '日历' else event['calendar']
        start_date = event['start_date'].strftime('%Y年%m月%d日 %H:%M:%S')
        end_date = event['end_date'].strftime('%Y年%m月%d日 %H:%M:%S')
        output += f"{calendar_name}|{event['summary']}|{start_date}|{end_date}\n"
    
    # 保存到文件
    with open('./calendar_export.csv', 'w', encoding='utf-8') as f:
        f.write(output)
    
    return True

# def main():
#     if get_calendar_events():
#         print("日历数据导出成功")
#     else:
#         print("日历数据导出失败")

# if __name__ == "__main__":
#     main()
#     print('test')