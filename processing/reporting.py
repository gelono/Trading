import matplotlib.pyplot as plt


def plot_results(table, trades_buy: list, lst_date_buy: list, trades_sell: list, lst_date_sell: list):
    dates_list = table['date'].to_list()
    plot_buy = []
    plot_sell = []
    plot_total = []
    plot_total_dates = []
    cum = 0
    for i in range(len(trades_buy)):
        cum = cum + trades_buy[i]
        plot_buy.append(cum)

    cum = 0
    for i in range(len(trades_sell)):
        cum = cum + trades_sell[i]
        plot_sell.append(cum)

    cum_t = 0
    for i in range(len(dates_list)):
        if dates_list[i] in lst_date_buy:
            index = lst_date_buy.index(dates_list[i])
            res = trades_buy[index]
            cum_t = cum_t + res
            plot_total.append(cum_t)
            plot_total_dates.append(dates_list[i])
        if dates_list[i] in lst_date_sell:
            index = lst_date_sell.index(dates_list[i])
            res = trades_sell[index]
            cum_t = cum_t + res
            plot_total.append(cum_t)
            plot_total_dates.append(dates_list[i])

    fig = plt.figure(figsize=(14, 10))
    plt.subplot(2, 2, 1)
    plt.plot(lst_date_buy, plot_buy)
    plt.title('Buy')
    plt.grid()

    plt.subplot(2, 2, 2)
    plt.plot(lst_date_sell, plot_sell)
    plt.title('Sell')
    plt.grid()

    plt.subplot(2, 2, 3)
    plt.plot(plot_total_dates, plot_total)
    plt.title('Total')
    plt.grid()
    plt.show()


def report_by_year(data: list, direction: str):
    dct = {
        2017: ([], []),
        2018: ([], []),
        2019: ([], []),
        2020: ([], []),
        2021: ([], []),
        2022: ([], []),
        2023: ([], [])
    }
    for e in data:
        year = e[0].date().year
        dct[year][0].append(e[1])
        dct[year][1].append(1)

    for key in dct:
        print(direction, str(key), round(sum(dct[key][0]), 2), '| trades: ', sum(dct[key][1]))