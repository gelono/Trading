import numpy

from processing.ta import *
from processing.trade_actions import *


def processing_buy_trades(table, table_week, delay_days, momentum, atr: int, koef, avg_price_days, week_atr_period):
    trade_actions = TradeActions(table)
    date_week_list = table_week['week_date'].to_list()
    last_week = date_week_list[-1]
    processing_limit = trade_actions.date_list.index(last_week)
    day = 40
    results = []

    while day < processing_limit + 1:
        if trade_actions.early_enter_buy(day):  # or late_enter_buy(table, day): # early_enter_buy
            date_of_trade = trade_actions.date_list[day]
            atr_week = week_ma_envelop(table_week, date_of_trade, week_atr_period, 1)
            if trade_actions.close_list[day] >= trade_actions.ma3x3_week_list[day] * (1 + atr_week):
                trade_category = 'high risk'
            else:
                trade_category = 'low risk'

            atr_avg = []
            for atr_ind in range(atr):
                atr_avg.append((trade_actions.high_list[day - atr_ind] - trade_actions.min_list[day - atr_ind]) /
                               trade_actions.min_list[day - atr_ind])
            stop_loss = numpy.mean(atr_avg)
            is_open_trade, trade_ind, open_price_buy, stop_price_buy = trade_actions.avg_enter_buy(results,
                            trade_actions.close_list, trade_actions.min_list, date_of_trade, trade_actions.date_list,
                            trade_actions.direction_list, trade_category, day, avg_price_days, stop_loss, koef)

            trade_ind += 1
            delay = False
            while is_open_trade:
                if delay is False:
                    is_open_trade, trade_ind, delay = trade_actions.processing_buy_delay(trade_ind, open_price_buy,
                        stop_price_buy, trade_actions.min_list, date_of_trade, trade_actions.date_list, trade_category,
                        trade_actions.direction_list, trade_actions.close_list, results, delay_days)
                    if is_open_trade and trade_actions.close_list[trade_ind - 1] > open_price_buy:
                        stop_price_buy = open_price_buy

                if is_open_trade:
                    is_open_trade, trade_ind = trade_actions.processing_buy_after_delay(trade_ind, open_price_buy,
                        stop_price_buy, trade_actions.min_list, date_of_trade, trade_actions.date_list, trade_category,
                        trade_actions.direction_list, trade_actions.close_list, results, momentum)

            day = trade_ind
        else:
            day += 1

    return results


def processing_sell_trades(table, table_week, delay_days, momentum, atr: int, koef, avg_price_days, week_atr_period):
    trade_actions = TradeActions(table)
    date_week_list = table_week['week_date'].to_list()
    last_week = date_week_list[-1]
    processing_limit = trade_actions.date_list.index(last_week)
    day = 40
    results = []

    while day < processing_limit + 1:
        if trade_actions.early_enter_sell(day):  # or late_enter_sell(table, day): # early_enter_sell
            date_of_trade = trade_actions.date_list[day]
            atr_week = week_ma_envelop(table_week, date_of_trade, week_atr_period, 1)
            if trade_actions.close_list[day] <= trade_actions.ma3x3_week_list[day] * (1 - atr_week):
                trade_category = 'high risk'
            else:
                trade_category = 'low risk'

            atr_avg = []
            for atr_ind in range(atr):
                atr_avg.append((trade_actions.high_list[day - atr_ind] - trade_actions.min_list[day - atr_ind]) /
                               trade_actions.min_list[day - atr_ind])
            stop_loss = numpy.mean(atr_avg)

            is_open_trade, trade_ind, open_price_sell, stop_price_sell = trade_actions.avg_enter_sell(results,
                            trade_actions.close_list, trade_actions.min_list, date_of_trade, trade_actions.date_list,
                            trade_actions.direction_list, trade_category, day, avg_price_days, stop_loss, koef)
            trade_ind += 1
            delay = False
            while is_open_trade:
                if delay is False:
                    is_open_trade, trade_ind, delay = trade_actions.processing_sell_delay(trade_ind, open_price_sell,
                        stop_price_sell, trade_actions.high_list, date_of_trade, trade_actions.date_list, trade_category,
                        trade_actions.direction_list, trade_actions.close_list, results, delay_days)
                    if is_open_trade and trade_actions.close_list[trade_ind - 1] < open_price_sell:
                        stop_price_sell = open_price_sell

                if is_open_trade:
                    is_open_trade, trade_ind = trade_actions.processing_sell_after_delay(trade_ind, open_price_sell,
                        stop_price_sell, trade_actions.high_list, date_of_trade, trade_actions.date_list, trade_category,
                        trade_actions.direction_list, trade_actions.close_list, results, momentum)

            day = trade_ind
        else:
            day += 1

    return results
