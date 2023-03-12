import pandas as pd
import numpy as np


class ProcessingData:
    COLUMNS = ['date', 'close', 'open', 'high', 'min', 'vol', 'change']
    DROP_COL = ['vol', 'change']
    PRICES = ['close', 'open', 'high', 'min']
    WEEK_COLS = ['week_date', 'week_close', 'week_high', 'week_low']

    def __init__(self, file: str, crypto: bool = True, week_ma_len: int = 3, week_ma_shift: int = 3):
        self.file = file
        self.crypto = crypto
        self.week_ma_len = week_ma_len
        self.week_ma_shift = week_ma_shift
        self.last_day_of_work_week = 6 if self.crypto else 4
        self.table = self.read_data(self.file, self.COLUMNS, self.DROP_COL, self.crypto, self.last_day_of_work_week,
                                    self.week_ma_len, self.week_ma_shift)
        self.table_week = self.table_week_create(self.table, 'date', 'closeofweak_temp', 'high', 'min',
                                                 self.last_day_of_work_week + 1)

    def read_data(self, file, columns: list, drop_col: list, crypto: bool, last_day_of_work_week: int, week_ma_len: int,
                  week_ma_shift: int):
        table = pd.read_csv(file, header=0)
        table.columns = columns
        table = table.drop(drop_col, axis=1)

        table = self.formatting_dates(table, 'date')
        table = self.columns_format_to_float(table, self.PRICES)
        table = self.sort_data_by_date(table)

        table['dayofweek'] = table['date'].dt.dayofweek
        if not crypto:
            table = table.drop(np.where(table['dayofweek'] == 5)[0])
            table = table.reset_index(drop=True)
            table = table.drop(np.where(table['dayofweek'] == 6)[0])
            table = table.reset_index(drop=True)

        table['closeofweak_temp'] = self.closeofweak_temp_create(table, last_day_of_work_week)
        table['ma_week_shift'] = self.calculate_ma_week(table, 'date', 'closeofweak_temp', week_ma_len, week_ma_shift)
        table['ma_week_shift'] = self.ma_week_filling(table)

        close = table['close'].to_frame()
        table['ma3x3_day'] = close['close'].rolling(3).mean()
        table['ma3x3_day'] = table['ma3x3_day'].shift(3)
        table['ma3x3_day'].fillna(0, inplace=True)

        table['direction'] = self.direction(table, 'closeofweak_temp', 'ma_week_shift')
        table.to_excel('table_save.xlsx')

        return table

    @staticmethod
    def formatting_dates(table, col_format: str):
        table[col_format] = pd.to_datetime(table[col_format], format='%d.%m.%Y')

        return table

    @staticmethod
    def columns_format_to_float(table, columns):
        for col in columns:
            table[col] = table[col].apply(lambda x: x.replace('.', '').replace(',', '.'))
            table[col] = table[col].astype(float)

        return table

    @staticmethod
    def sort_data_by_date(table):
        table = table.sort_index(ascending=False)
        table = table.reset_index()
        table = table.drop('index', axis=1)

        return table

    @staticmethod
    def fill_column_with_shift(table, column: str, days) -> list:
        temp_list = table[column].to_list()
        len_lst = len(temp_list)
        new_column = [0] * len_lst
        for i in range(len_lst):
            if temp_list[i] != 0:
                for j in range(i + 1, i + days):
                    try:
                        new_column[j] = temp_list[i]
                    except IndexError:
                        break

        return new_column

    @staticmethod
    def closeofweak_temp_create(table, last_day_of_work_week):
        closeofweak_temp = [0] * table.shape[0]
        closes = table['close'].to_list()
        daysofweek = table['dayofweek'].to_list()
        for i in range(1, table.shape[0]):  # (daysofweek[i] == 0 and daysofweek[i - 1] == last_day_of_work_week)
            if daysofweek[i] == last_day_of_work_week:
                closeofweak_temp[i] = closes[i]
            elif daysofweek[i] == 0 and daysofweek[i - 1] == last_day_of_work_week - 1:
                closeofweak_temp[i - 1] = closes[i - 1]

        return closeofweak_temp

    @staticmethod
    def calculate_ma_week(table, date_col: str, close_col: str, ma_len, ma_shift):
        date_list = table[date_col].to_list()
        closeofweak_temp_list = table[close_col].to_list()
        clean_cl_list = {}
        for d, c in zip(date_list, closeofweak_temp_list):
            if c != 0:
                clean_cl_list[d] = c

        ma = {}
        list_pairs = list(clean_cl_list.items())
        for i in range(ma_len - 1, len(list_pairs)):
            if i - (ma_len - 1) == 0:
                for j in range(ma_len - 1):
                    ma[list_pairs[j][0]] = 0
            ma_data = []
            for k in range(ma_len):
                ma_data.append(list_pairs[i - k][1])
            ma_val = np.mean(ma_data)
            ma[list_pairs[i][0]] = ma_val

        df = pd.DataFrame(list(ma.values()), columns=['ma_week_shift'])
        df['ma_week_shift'] = df['ma_week_shift'].shift(ma_shift)
        df['ma_week_shift'].fillna(0, inplace=True)
        ma_week_shift = df['ma_week_shift'].to_list()

        keys = list(ma.keys())
        for i in range(len(keys)):
            ma[keys[i]] = ma_week_shift[i]

        ma_list = [0] * table.shape[0]
        for i in range(table.shape[0]):
            if date_list[i] in ma.keys():
                ma_list[i] = ma[date_list[i]]

        table['ma_week_shift'] = ma_list
        # table['ma_week_shift'] = table['ma_week_shift'].shift(ma_shift * days_in_week)  # 21,  non crypto - 15
        # table['ma_week_shift'].fillna(0, inplace=True)

        return table['ma_week_shift'].to_list()

    @staticmethod
    def ma_week_filling(table):
        ma3x3_w_l = table['ma_week_shift'].to_list()
        new_ma3x3_w = [0] * table.shape[0]
        for i in range(table.shape[0]):
            if ma3x3_w_l[i] != 0:
                new_ma3x3_w[i] = ma3x3_w_l[i]
                j = i - 1
                while j > 7 and ma3x3_w_l[j] == 0:
                    new_ma3x3_w[j] = ma3x3_w_l[i]
                    j -= 1

        return new_ma3x3_w

    @staticmethod
    def direction(table, close_week_col: str, ma3x3_week_col: str):
        close_of_week_list = table[close_week_col].to_list()
        ma3x3_week_list = table[ma3x3_week_col].to_list()
        direction_list = [0] * table.shape[0]
        for i in range(table.shape[0]):
            if ma3x3_week_list[i] != 0 and close_of_week_list[i] > ma3x3_week_list[i]:
                for j in range(i, i + 8):
                    try:
                        direction_list[j] = 1
                    except IndexError:
                        break

        return direction_list

    def table_week_create(self, table, date_col, week_close_col, day_high_col, day_low_col, days_in_week):
        date_col_list = table[date_col].to_list()
        close_week_list = table[week_close_col].to_list()
        high_list = table[day_high_col].to_list()
        low_list = table[day_low_col].to_list()

        date_week = []
        close_week = []
        high_week = []
        low_week = []

        for i in range(days_in_week, table.shape[0]):
            if close_week_list[i] != 0:
                temp_high_list = []
                temp_low_list = []
                k = i - 1
                count = 0
                while close_week_list[k] == 0:
                    count += 1
                    k -= 1
                for j in range(i - count, i + 1):
                    temp_high_list.append(high_list[j])
                    temp_low_list.append(low_list[j])
                date_week.append(date_col_list[i])
                close_week.append(close_week_list[i])
                high_week.append(max(temp_high_list))
                low_week.append(min(temp_low_list))

        table_week = pd.DataFrame(columns=self.WEEK_COLS)
        table_week['week_date'] = date_week
        table_week['week_close'] = close_week
        table_week['week_high'] = high_week
        table_week['week_low'] = low_week

        return table_week
