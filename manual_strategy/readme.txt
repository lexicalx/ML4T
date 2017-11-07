Please follow the instructions in this file to run manual_strategy code:

1) Run "python indicators.py" on the command line to generate all the charts for the indicators
2) Run "python BestPossibleStrategy.py" on the command line to generate the best possible strategy trade_df, submit it to marketsimcode, and plot charts
3) In-sample
3.1) Edit ManualStrategy.py line 154 and 155 to change the dates for in-sample period to
    sd = dt.datetime(2008, 1, 1) - Line 154
    ed = dt.datetime(2009, 12, 31) - Line 155
    benchmark_df = ms.testBenchMark(symbol='JPM',sd=sd+ dt.timedelta(days=1),ed=ed,sv=sv) - Line 159
3.2)  Edit ManualStrategy.py line 181 for the in-sample period to
    plot_portvals(ms,benchmark_portvals, ms_portvals, 'insample')
3.2) Run "python ManualStrategy.py" on the command line to generate the manual rule based strategy trade_df, submit it to marketsimcode, and plot charts for in-sample data

4) Out-sample
4.1) Edit ManualStrategy.py line 154 and 155 to change the dates for out-sample period to
    sd = dt.datetime(2010, 1, 1)- Line 154
    ed = dt.datetime(2011, 12, 31)- Line 155
    benchmark_df = ms.testBenchMark(symbol='JPM',sd=sd+ dt.timedelta(days=3),ed=ed,sv=sv) - Line 159
4.2)  Edit ManualStrategy.py line 181 for the out-sample period to
    plot_portvals(ms,benchmark_portvals, ms_portvals, 'outsample')
4.2) Run "python ManualStrategy.py" on the command line to generate the manual rule based strategy trade_df, submit it to marketsimcode, and plot charts for out-sample data
