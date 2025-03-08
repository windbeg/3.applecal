on run argv
    -- 处理命令行参数
    set startDateStr to ""
    set sourceCalendarTypes to {"个人", "日历", "工作", "读书"}
    set targetCalendarTypes to {"个人", "放松", "工作", "读书"}
    
    -- 解析日期参数
    if (count of argv) > 0 then
        set startDateStr to item 1 of argv
    end if
    
    -- 解析源日历类型列表
    if (count of argv) > 1 then
        set sourceCalendarStr to item 2 of argv
        set sourceCalendarTypes to my splitString(sourceCalendarStr, "|") 
    end if
    
    -- 解析目标日历类型列表
    if (count of argv) > 2 then
        set targetCalendarStr to item 3 of argv
        set targetCalendarTypes to my splitString(targetCalendarStr, "|")
    end if
    
tell application "Calendar"
    -- 设置时间范围
    set currentDate to current date
    
    -- 如果有传入日期参数，则使用该日期作为起始日期，否则使用一年前的日期
    set startDate to currentDate - (210 * days)
    if startDateStr is not "" then
        -- 解析传入的日期字符串 (格式为 YYYY-MM-DD)
        set y to text 1 thru 4 of startDateStr as integer
        set m to text 6 thru 7 of startDateStr as integer
        set d to text 9 thru 10 of startDateStr as integer
        
        -- 正确构造日期对象
        set startDate to current date
        set year of startDate to y
        set month of startDate to m
        set day of startDate to d
        set hours of startDate to 0
        set minutes of startDate to 0
        set seconds of startDate to 0
    end if
    
    -- 初始化日历和事件列表
    set calendarList to {}
    set eventsList to {}
    
    -- 获取所有指定的日历和事件
    repeat with i from 1 to count of sourceCalendarTypes
        set calendarName to item i of sourceCalendarTypes
        set end of calendarList to calendar calendarName
        set end of eventsList to (every event of (item -1 of calendarList) whose start date is greater than or equal to startDate)
    end repeat

    set theOutput to "Calendar|Summary|Start Date|End Date\n"
    
    -- 处理所有事件
    repeat with i from 1 to count of eventsList
        set currentEvents to item i of eventsList
        set targetCalendarName to item i of targetCalendarTypes
        
        repeat with theEvent in currentEvents
            set startDate to start date of theEvent
            set endDate to end date of theEvent
            set theOutput to theOutput & targetCalendarName & "|" & my escapeCSV(summary of theEvent) & "|" & my formatDate(startDate) & "|" & my formatDate(endDate) & "\n"
        end repeat
    end repeat


    do shell script "echo " & quoted form of theOutput & " > ./calendar_export.csv"
    
end tell
end run

on formatDate(theDate)
    set dateString to date string of theDate
    set timeString to time string of theDate
    return dateString & " " & timeString
end formatDate

on escapeCSV(theText)
    set escapedText to quoted form of theText
    return text 2 thru -2 of escapedText -- remove the surrounding quotes
end escapeCSV

on splitString(theString, theDelimiter)
    set oldDelimiters to AppleScript's text item delimiters
    set AppleScript's text item delimiters to theDelimiter
    set theArray to every text item of theString
    set AppleScript's text item delimiters to oldDelimiters
    return theArray
end splitString
