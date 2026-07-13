let
    StartDate = #date(2022, 1, 1),
    EndDate = #date(2025, 6, 30),
    Dates = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    ToTable = Table.FromList(Dates, Splitter.SplitByNothing(), null, null, ExtraValues.Error),
    Renamed = Table.RenameColumns(ToTable, {{"Column1", "Date"}}),
    #"Changed Type" = Table.TransformColumnTypes(Renamed, {{"Date", type date}}),
    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Quarter" = Table.AddColumn(#"Added Year", "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    #"Added Month" = Table.AddColumn(#"Added Quarter", "Month", each Date.MonthName([Date]), type text),
    #"Added MonthNo" = Table.AddColumn(#"Added Month", "MonthNo", each Date.Month([Date]), Int64.Type),
    #"Added YearMonth" = Table.AddColumn(#"Added MonthNo", "YearMonth", each Text.From(Date.Year([Date])) & "-" & Text.PadStart(Text.From(Date.Month([Date])), 2, "0"), type text),
    #"Added Weekday" = Table.AddColumn(#"Added YearMonth", "Weekday", each Date.DayOfWeekName([Date]), type text),
    #"Added IsWeekend" = Table.AddColumn(#"Added Weekday", "IsWeekend", each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical)
in
    #"Added IsWeekend