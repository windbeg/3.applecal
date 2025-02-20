tell application "Calendar" to activate

tell application "Calendar"
    set personalCalendar to calendar "个人"
    set pornCalendar to calendar "日历"
    set workCalendar to calendar "工作"

    set personalEvents to every event of personalCalendar
    set pornEvents to every event of pornCalendar
    set workEvents to every event of workCalendar

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

    repeat with theEvent in workEvents
        set startDate to start date of theEvent
        set endDate to end date of theEvent
        set theOutput to theOutput & "工作|" & my escapeCSV(summary of theEvent) & "|" & my formatDate(startDate) & "|" & my formatDate(endDate) & "\n"
    end repeat
    

    do shell script "echo " & quoted form of theOutput & " > ~/trae/3.applecal/calendar_export.csv"
    
end tell

on formatDate(theDate)
    set dateString to date string of theDate
    set timeString to time string of theDate
    return dateString & " " & timeString
end formatDate

on escapeCSV(theText)
    set escapedText to quoted form of theText
    return text 2 thru -2 of escapedText -- remove the surrounding quotes
end escapeCSV