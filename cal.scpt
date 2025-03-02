on run argv
    -- 处理命令行参数
    set startDateStr to ""
    if (count of argv) > 0 then
        set startDateStr to item 1 of argv
    end if
    
tell application "Calendar"
    -- 设置时间范围
    set currentDate to current date
    
    -- 如果有传入日期参数，则使用该日期作为起始日期，否则使用一年前的日期
    set startDate to currentDate - (365 * days)
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
    
    set personalCalendar to calendar "个人"
    set pornCalendar to calendar "日历"
    set workCalendar to calendar "工作"
    set readingCalendar to calendar "读书"

    -- 获取过滤后的事件
    set personalEvents to (every event of personalCalendar whose start date is greater than or equal to startDate)
    set pornEvents to (every event of pornCalendar whose start date is greater than or equal to startDate)
    set workEvents to (every event of workCalendar whose start date is greater than or equal to startDate)
    set readingEvents to (every event of readingCalendar whose start date is greater than or equal to startDate)

    set theOutput to "Calendar|Summary|Start Date|End Date\n"
    
    repeat with theEvent in personalEvents
        set startDate to start date of theEvent
        set endDate to end date of theEvent
        set theOutput to theOutput & "个人|" & my escapeCSV(summary of theEvent) & "|" & my formatDate(startDate) & "|" & my formatDate(endDate) & "\n"
    end repeat
    
    repeat with theEvent in pornEvents
        set startDate to start date of theEvent
        set endDate to end date of theEvent
        set theOutput to theOutput & "放松|" & my escapeCSV(summary of theEvent) & "|" & my formatDate(startDate) & "|" & my formatDate(endDate) & "\n"
    end repeat

    repeat with theEvent in readingEvents
        set startDate to start date of theEvent
        set endDate to end date of theEvent
        set theOutput to theOutput & "读书|" & my escapeCSV(summary of theEvent) & "|" & my formatDate(startDate) & "|" & my formatDate(endDate) & "\n"
    end repeat

    repeat with theEvent in workEvents
        set startDate to start date of theEvent
        set endDate to end date of theEvent
        set theOutput to theOutput & "工作|" & my escapeCSV(summary of theEvent) & "|" & my formatDate(startDate) & "|" & my formatDate(endDate) & "\n"
    end repeat


    do shell script "echo " & quoted form of theOutput & " > ~/trae/3.applecal/calendar_export.csv"
    
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