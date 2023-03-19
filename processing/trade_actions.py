import numpy as np


class TradeActions:
    table = None
    date_list: list = None
    close_list: list = None
    high_list: list = None
    min_list: list = None
    direction_list: list = None
    ma3x3_week_list: list = None

    def __init__(self, table):
        self.table = table
        self.date_list = table['date'].to_list()
        self.close_list = table['close'].to_list()
        self.high_list = table['high'].to_list()
        self.min_list = table['min'].to_list()
        self.direction_list = table['direction'].to_list()
        self.ma3x3_week_list = table['ma_week_shift'].to_list()

    def early_enter_buy(self, day):
        if self.table['direction'][day] == 1 \
                and self.table['close'][day] < self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] >= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] > self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def late_enter_buy(self, day):
        if self.table['direction'][day] == 1 \
                and self.table['close'][day] > self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] <= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] > self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def early_enter_sell(self, day):
        if self.table['direction'][day] == 0 \
                and self.table['close'][day] > self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] <= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] < self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def late_enter_sell(self, day):
        if self.table['direction'][day] == 0 \
                and self.table['close'][day] < self.table['ma3x3_day'][day] \
                and self.table['close'][day - 1] >= self.table['ma3x3_day'][day - 1] \
                and self.table['close'][day] < self.table['ma_week_shift'][day]:
            return True
        else:
            return False

    def avg_enter_buy(self, results, date_of_trade, trade_category, day, avg_price_days, stop_loss, koef):
        price_list = [self.close_list[day]]
        open_price_buy = np.mean(price_list)
        stop_price_buy = open_price_buy * (1-(stop_loss*koef))
        count = 1
        for i in range(day + 1, day + avg_price_days):
            try:
                if self.min_list[i] <= stop_price_buy:
                    result = (date_of_trade, (((stop_price_buy - open_price_buy) / open_price_buy) * 100) *
                              (count / avg_price_days), self.date_list[i], stop_price_buy, 'Stop-loss', trade_category)
                    results.append(result)
                    return False, i, open_price_buy, stop_price_buy
                elif self.direction_list[i] == 0:
                    result = (date_of_trade, (((self.close_list[i] - open_price_buy) / open_price_buy) * 100)
                              * (count / avg_price_days), self.date_list[i], stop_price_buy, 'Direction has changed',
                              trade_category)
                    results.append(result)
                    return False, i, open_price_buy, stop_price_buy
                else:
                    price_list.append(self.close_list[i])
                    open_price_buy = np.mean(price_list)
                    stop_price_buy = open_price_buy * (1-(stop_loss*koef))
                    count += 1
                    day = i
            except IndexError:
                result = (date_of_trade, (((self.close_list[-1] - open_price_buy) / open_price_buy) * 100) *
                          (count / avg_price_days), self.date_list[-1], stop_price_buy, 'End of the data',
                          trade_category)
                results.append(result)
                return False, i, open_price_buy, stop_price_buy

        return True, day, open_price_buy, stop_price_buy

    def avg_enter_sell(self, results, date_of_trade, trade_category, day, avg_price_days, stop_loss, koef):
        price_list = [self.close_list[day]]
        open_price_sell = np.mean(price_list)
        stop_price_sell = open_price_sell * (1 + (stop_loss * koef))
        count = 1
        for i in range(day + 1, day + avg_price_days):
            try:
                if self.high_list[i] >= stop_price_sell:
                    result = (
                        date_of_trade, (((open_price_sell - stop_price_sell) / open_price_sell) * 100) *
                        (count / avg_price_days), self.date_list[i], stop_price_sell, 'Stop-loss', trade_category
                    )
                    results.append(result)
                    return False, i, open_price_sell, stop_price_sell
                elif self.direction_list[i] == 1:
                    result = (date_of_trade, (((open_price_sell - self.close_list[i]) / open_price_sell) * 100)
                              * (count / avg_price_days), self.date_list[i], stop_price_sell, 'Direction has changed',
                              trade_category)
                    results.append(result)
                    return False, i, open_price_sell, stop_price_sell
                else:
                    price_list.append(self.close_list[i])
                    open_price_sell = np.mean(price_list)
                    stop_price_sell = open_price_sell * (1 + (stop_loss * koef))
                    count += 1
                    day = i
            except IndexError:
                result = (date_of_trade, (((open_price_sell - self.close_list[-1]) / open_price_sell) * 100) *
                          (count / avg_price_days), self.date_list[-1], stop_price_sell, 'End of the data',
                          trade_category)
                results.append(result)
                return False, i, open_price_sell, stop_price_sell

        return True, day, open_price_sell, stop_price_sell

    def processing_buy_delay(self, trade_ind, open_price_buy, stop_price_buy, date_of_trade, trade_category,
                             results, delay_days):
        is_open_trade = True
        for i in range(trade_ind, trade_ind + delay_days):
            try:
                if self.min_list[i] <= stop_price_buy:
                    result = (
                        date_of_trade, ((stop_price_buy - open_price_buy) / open_price_buy) * 100,
                        self.date_list[i], stop_price_buy, 'Stop-loss', trade_category
                    )
                    is_open_trade = False
                    results.append(result)
                    trade_ind = i + 1
                    break
                elif self.direction_list[i] == 0:
                    result = (
                        date_of_trade, ((self.close_list[i] - open_price_buy) / open_price_buy) * 100,
                        self.date_list[i], self.close_list[i], 'Direction has changed', trade_category
                    )
                    is_open_trade = False
                    results.append(result)
                    trade_ind = i + 1
                    break
                trade_ind = i + 1
            except IndexError:
                result = (
                    date_of_trade, ((self.close_list[self.table.shape[0] - 1] - open_price_buy) / open_price_buy) * 100,
                    self.date_list[self.table.shape[0] - 1], self.close_list[self.table.shape[0] - 1],
                    'End of the data', trade_category
                )
                is_open_trade = False
                results.append(result)
                trade_ind = i + 1
                break

        delay = True
        return is_open_trade, trade_ind, delay

    def processing_sell_delay(self, trade_ind, open_price_sell, stop_price_sell, date_of_trade, trade_category,
                              results, delay_days):
        is_open_trade = True
        for i in range(trade_ind, trade_ind + delay_days):
            try:
                if self.high_list[i] >= stop_price_sell:
                    result = (
                        date_of_trade, ((open_price_sell - stop_price_sell) / open_price_sell) * 100,
                        self.date_list[i], stop_price_sell, 'Stop-loss', trade_category
                    )
                    is_open_trade = False
                    results.append(result)
                    trade_ind = i + 1
                    break
                elif self.direction_list[i] == 1:
                    result = (
                        date_of_trade, ((open_price_sell - self.close_list[i]) / open_price_sell) * 100,
                        self.date_list[i], self.close_list[i], 'Direction has changed', trade_category
                    )
                    is_open_trade = False
                    results.append(result)
                    trade_ind = i + 1
                    break
                trade_ind = i + 1
            except IndexError:
                result = (
                    date_of_trade, ((open_price_sell - self.close_list[self.table.shape[0] - 1]) / open_price_sell) *
                    100, self.date_list[self.table.shape[0] - 1], self.close_list[self.table.shape[0] - 1],
                    'End of the data', trade_category
                )
                is_open_trade = False
                results.append(result)
                trade_ind = i + 1
                break

        delay = True
        return is_open_trade, trade_ind, delay

    def processing_buy_after_delay(self, trade_ind, open_price_buy, stop_price_buy, date_of_trade, trade_category,
                                   results, momentum):
        is_open_trade = True
        try:
            if self.min_list[trade_ind] <= stop_price_buy:
                result = (
                    date_of_trade, ((stop_price_buy - open_price_buy) / open_price_buy) * 100,
                    self.date_list[trade_ind],
                    stop_price_buy, 'Stop-loss', trade_category
                )
                is_open_trade = False
                results.append(result)
                trade_ind += 1
            elif self.direction_list[trade_ind] == 0:
                result = (
                    date_of_trade, ((self.close_list[trade_ind] - open_price_buy) / open_price_buy) * 100,
                    self.date_list[trade_ind], self.close_list[trade_ind], 'Direction has changed', trade_category
                )
                is_open_trade = False
                results.append(result)
                trade_ind += 1
            else:
                mom_3 = self.close_list[trade_ind] - self.close_list[trade_ind - momentum]
                if mom_3 < 0:
                    result = (
                        date_of_trade, ((self.close_list[trade_ind] - open_price_buy) / open_price_buy) * 100,
                        self.date_list[trade_ind], self.close_list[trade_ind], 'Exit by MOM-3', trade_category
                    )
                    is_open_trade = False
                    results.append(result)
                trade_ind += 1
        except IndexError:
            result = (
                date_of_trade, ((self.close_list[self.table.shape[0] - 1] - open_price_buy) / open_price_buy) * 100,
                self.date_list[self.table.shape[0] - 1], self.close_list[self.table.shape[0] - 1], 'End of the data',
                trade_category
            )
            is_open_trade = False
            results.append(result)
            trade_ind += 1

        return is_open_trade, trade_ind

    def processing_sell_after_delay(self, trade_ind, open_price_sell, stop_price_sell, date_of_trade, trade_category,
                                    results, momentum):
        is_open_trade = True
        try:
            if self.high_list[trade_ind] >= stop_price_sell:
                result = (
                    date_of_trade, ((open_price_sell - stop_price_sell) / open_price_sell) * 100,
                    self.date_list[trade_ind], stop_price_sell, 'Stop-loss', trade_category
                )
                is_open_trade = False
                results.append(result)
                trade_ind += 1
            elif self.direction_list[trade_ind] == 1:
                result = (
                    date_of_trade, ((open_price_sell - self.close_list[trade_ind]) / open_price_sell) * 100,
                    self.date_list[trade_ind], self.close_list[trade_ind], 'Direction has changed', trade_category
                )
                is_open_trade = False
                results.append(result)
                trade_ind += 1
            else:
                mom_3 = self.close_list[trade_ind] - self.close_list[trade_ind - momentum]
                if mom_3 > 0:
                    result = (
                        date_of_trade, ((open_price_sell - self.close_list[trade_ind]) / open_price_sell) * 100,
                        self.date_list[trade_ind], self.close_list[trade_ind], 'Exit by MOM-3', trade_category
                    )
                    is_open_trade = False
                    results.append(result)
                trade_ind += 1
        except IndexError:
            result = (
                date_of_trade, ((open_price_sell - self.close_list[self.table.shape[0] - 1]) / open_price_sell) * 100,
                self.date_list[self.table.shape[0] - 1], self.close_list[self.table.shape[0] - 1], 'End of the data',
                trade_category
            )
            is_open_trade = False
            results.append(result)
            trade_ind += 1

        return is_open_trade, trade_ind