import numpy

from processing.ta import *
from processing.trade_actions import *


def processing_buy_trades(table, table_week, delay_days, momentum, atr: int, koef, avg_price_days, week_atr_period):
    date_list = table['date'].to_list()
    close_list = table['close'].to_list()
    high_list = table['high'].to_list()
    min_list = table['min'].to_list()
    # ma3x3_day_list = table['ma3x3_day'].to_list()
    ma3x3_week_list = table['ma_week_shift'].to_list()
    direction_list = table['direction'].to_list()

    date_week_list = table_week['week_date'].to_list()
    last_week = date_week_list[-1]
    processing_limit = date_list.index(last_week)
    day = 40
    results = []
    trade_actions = TradeActions(table)

    while day < processing_limit + 1:
        if trade_actions.early_enter_buy(day):  # or late_enter_buy(table, day): # early_enter_buy
            # is_open_trade = True
            date_of_trade = date_list[day]
            atr_week = week_ma_envelop(table_week, date_of_trade, week_atr_period, 1)
            if close_list[day] >= ma3x3_week_list[day] * (1 + atr_week):
                trade_category = 'high risk'
            else:
                trade_category = 'low risk'

            atr_avg = []
            for atr_ind in range(atr):
                atr_avg.append((high_list[day - atr_ind] - min_list[day - atr_ind]) / min_list[day - atr_ind])
            stop_loss = numpy.mean(atr_avg)
            is_open_trade, trade_ind, open_price_buy, stop_price_buy = trade_actions.avg_enter_buy(results, close_list,
                                                                                                   min_list,
                                                                                                   date_of_trade,
                                                                                                   date_list,
                                                                                                   direction_list,
                                                                                                   trade_category, day,
                                                                                                   avg_price_days,
                                                                                                   stop_loss, koef)

            trade_ind += 1
            delay = False
            while is_open_trade:
                if delay is False:
                    is_open_trade, trade_ind, delay = trade_actions.processing_buy_delay(trade_ind, open_price_buy,
                        stop_price_buy, min_list, date_of_trade, date_list, trade_category, direction_list, close_list,
                        results, delay_days)
                    if is_open_trade and close_list[trade_ind - 1] > open_price_buy:
                        stop_price_buy = open_price_buy

                if is_open_trade:
                    is_open_trade, trade_ind = trade_actions.processing_buy_after_delay(trade_ind, open_price_buy,
                                                stop_price_buy, min_list, date_of_trade, date_list, trade_category,
                                                direction_list, close_list, results, momentum)
                    # try:
                    #     if min_list[trade_ind] <= stop_price_buy:
                    #         result = (
                    #             date_of_trade, ((stop_price_buy - open_price_buy) / open_price_buy) * 100,
                    #             date_list[trade_ind],
                    #             stop_price_buy, 'Stop-loss', trade_category
                    #         )
                    #         is_open_trade = False
                    #         results.append(result)
                    #         trade_ind += 1
                    #     elif direction_list[trade_ind] == 0:
                    #         result = (
                    #             date_of_trade, ((close_list[trade_ind] - open_price_buy) / open_price_buy) * 100,
                    #             date_list[trade_ind], close_list[trade_ind], 'Direction has changed', trade_category
                    #         )
                    #         is_open_trade = False
                    #         results.append(result)
                    #         trade_ind += 1
                    #     else:
                    #         mom_3 = close_list[trade_ind] - close_list[trade_ind - momentum]
                    #         if mom_3 < 0:
                    #             result = (
                    #                 date_of_trade, ((close_list[trade_ind] - open_price_buy) / open_price_buy) * 100,
                    #                 date_list[trade_ind], close_list[trade_ind], 'Exit by MOM-3', trade_category
                    #             )
                    #             is_open_trade = False
                    #             results.append(result)
                    #         trade_ind += 1
                    # except IndexError:
                    #     result = (
                    #         date_of_trade,
                    #         ((close_list[table.shape[0] - 1] - open_price_buy) / open_price_buy) * 100,
                    #         date_list[table.shape[0] - 1], close_list[table.shape[0] - 1], 'End of the data',
                    #         trade_category
                    #     )
                    #     is_open_trade = False
                    #     results.append(result)
                    #     trade_ind += 1
            day = trade_ind
        else:
            day += 1

    return results


def processing_sell_trades(table, table_week, delay_days, momentum, atr: int, koef, avg_price_days, week_atr_period):
    date_list = table['date'].to_list()
    close_list = table['close'].to_list()
    high_list = table['high'].to_list()
    min_list = table['min'].to_list()
    # ma3x3_day_list = table['ma3x3_day'].to_list()
    ma3x3_week_list = table['ma_week_shift'].to_list()
    direction_list = table['direction'].to_list()

    date_week_list = table_week['week_date'].to_list()
    last_week = date_week_list[-1]
    processing_limit = date_list.index(last_week)
    day = 40
    results = []
    trade_actions = TradeActions(table)

    while day < processing_limit + 1:
        if trade_actions.early_enter_sell(day):  # or late_enter_sell(table, day): # early_enter_sell
            # is_open_trade = True
            date_of_trade = date_list[day]
            atr_week = week_ma_envelop(table_week, date_of_trade, week_atr_period, 1)
            if close_list[day] <= ma3x3_week_list[day] * (1 - atr_week):
                trade_category = 'high risk'
            else:
                trade_category = 'low risk'

            atr_avg = []
            for atr_ind in range(atr):
                atr_avg.append((high_list[day - atr_ind] - min_list[day - atr_ind]) / min_list[day - atr_ind])
            stop_loss = numpy.mean(atr_avg)

            is_open_trade, trade_ind, open_price_sell, stop_price_sell = trade_actions.avg_enter_sell(results,
                                                                                                      close_list,
                                                                                                      min_list,
                                                                                                      date_of_trade,
                                                                                                      date_list,
                                                                                                      direction_list,
                                                                                                      trade_category,
                                                                                                      day,
                                                                                                      avg_price_days,
                                                                                                      stop_loss,
                                                                                                      koef)
            trade_ind += 1
            delay = False
            while is_open_trade:
                if delay is False:
                    is_open_trade, trade_ind, delay = trade_actions.processing_sell_delay(trade_ind, open_price_sell,
                        stop_price_sell, high_list, date_of_trade, date_list, trade_category, direction_list,
                        close_list, results, delay_days)
                    if is_open_trade and close_list[trade_ind - 1] < open_price_sell:
                        stop_price_sell = open_price_sell

                if is_open_trade:
                    is_open_trade, trade_ind = trade_actions.processing_sell_after_delay(trade_ind, open_price_sell,
                                                stop_price_sell, high_list, date_of_trade, date_list, trade_category,
                                                direction_list, close_list, results, momentum)
                    # try:
                    #     if high_list[trade_ind] >= stop_price_sell:
                    #         result = (
                    #             date_of_trade, ((open_price_sell - stop_price_sell) / open_price_sell) * 100,
                    #             date_list[trade_ind],
                    #             stop_price_sell, 'Stop-loss', trade_category
                    #         )
                    #         is_open_trade = False
                    #         results.append(result)
                    #         trade_ind += 1
                    #     elif direction_list[trade_ind] == 1:
                    #         result = (
                    #             date_of_trade, ((open_price_sell - close_list[trade_ind]) / open_price_sell) * 100,
                    #             date_list[trade_ind], close_list[trade_ind], 'Direction has changed', trade_category
                    #         )
                    #         is_open_trade = False
                    #         results.append(result)
                    #         trade_ind += 1
                    #     else:
                    #         mom_3 = close_list[trade_ind] - close_list[trade_ind - momentum]
                    #         if mom_3 > 0:
                    #             result = (
                    #                 date_of_trade, ((open_price_sell - close_list[trade_ind]) / open_price_sell) * 100,
                    #                 date_list[trade_ind], close_list[trade_ind], 'Exit by MOM-3', trade_category
                    #             )
                    #             is_open_trade = False
                    #             results.append(result)
                    #         trade_ind += 1
                    # except IndexError:
                    #     result = (
                    #         date_of_trade,
                    #         ((open_price_sell - close_list[table.shape[0] - 1]) / open_price_sell) * 100,
                    #         date_list[table.shape[0] - 1], close_list[table.shape[0] - 1], 'End of the data',
                    #         trade_category
                    #     )
                    #     is_open_trade = False
                    #     results.append(result)
                    #     trade_ind += 1
            day = trade_ind
        else:
            day += 1

    return results
