let
    Source = Csv.Document(
        File.Contents("D:/SHIVAM/Documents/Data Analytics/swiftdash-ops-analytics/data/cleaned/orders_clean.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    #"Promoted Headers"