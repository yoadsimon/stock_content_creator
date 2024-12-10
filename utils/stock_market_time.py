import datetime

from utils.consts import MARKET_TIME_ZONE


class StockMarketTime:
    def __init__(self, mock_data_input_now=None):
        self.now = datetime.datetime.now(MARKET_TIME_ZONE)
        self.is_mock = False
        if mock_data_input_now:
            self.now = mock_data_input_now
            self.is_mock = True
        self.last_time_closed = self.get_last_time_closed_stock_market()
        self.next_time_open = self.get_next_time_open_stock_market()
        self.is_closed = self.next_time_open > self.last_time_closed
        self.is_open = not self.is_closed
        self.get_times()

    def get_last_time_closed_stock_market(self):
        # todo - make this function more advanced (include days in week and holidays)
        # for now return last day's 4pm if its before 4pm, else return today's 4pm
        market_close_time = self.now.replace(hour=16, minute=0, second=0, microsecond=0)
        return market_close_time - datetime.timedelta(days=1) if self.now < market_close_time else market_close_time

    def get_next_time_open_stock_market(self):
        # todo - make this function more advanced (include days in week and holidays)
        # for now return last day's 4pm if its before 4pm, else return today's 4pm
        market_open_time = self.now.replace(hour=9, minute=30, second=0, microsecond=0)
        return market_open_time + datetime.timedelta(days=1) if self.now > market_open_time else market_open_time

    def get_times(self):
        if self.next_time_open > self.last_time_closed:
            print(f"Stock market is closed, it will open next at: {self.next_time_open}")
            time_until_open = self.next_time_open - self.now
            hours, minutes = format_time_difference(time_until_open)
            print(f"In {hours} hours and {minutes} minutes")
        else:
            print(f"Stock market is open, it will close next at: {self.last_time_closed + datetime.timedelta(days=1)}")
            time_until_close = self.last_time_closed - self.now
            hours, minutes = format_time_difference(time_until_close)
            print(f"In {hours} hours and {minutes} minutes")
        return self.now, self.last_time_closed, self.next_time_open

def format_time_difference(delta):
    total_seconds = delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return int(hours), int(minutes)