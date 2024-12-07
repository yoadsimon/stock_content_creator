import time
import yfinance as yf
import datetime
import asyncio
import logging
from tqdm import tqdm
from utils.consts import MARKET_TIME_ZONE
from utils.open_ai import generate_stock_opening_analysis, summarize_with_open_ai
from utils.stock_market_time import StockMarketTime
from utils.utils import get_text_by_url, save_to_temp_file, read_temp_file, setup_logging

setup_logging()


def create_content(use_temp_file=False, mock_data_input_now=None) -> str:
    logging.info("Starting stock market time check...")
    stock_market_time = StockMarketTime(mock_data_input_now)
    stock_symbol = 'NVDA'
    company_name = 'NVIDIA Corporation'
    now_date = stock_market_time.now.strftime("%Y-%m-%d")

    file_name = f"{stock_symbol}_{now_date}"
    stock_info = read_temp_file(file_name) if use_temp_file else None

    if not stock_info:
        stock_info = get_stock_data(stock_symbol, company_name, stock_market_time)
        save_to_temp_file(stock_info, file_name)

    result = generate_stock_opening_analysis(stock_info, company_name, stock_symbol)
    return result


def get_stock_data(stock_symbol: str, company_name: str, stock_market_time: StockMarketTime) -> str:
    logging.info("Getting stock data...")
    price_data = get_price_data(stock_symbol, stock_market_time)
    logging.info("Getting news data...")
    news_data = get_news_data(company_name, stock_symbol, stock_market_time)
    logging.info("Preparing output...")
    return f"Stock Data for {company_name} ({stock_symbol}):\n\n" \
           f"Price Data:\n{price_data}\n\n" \
           f"News Data:\n{news_data}"


def get_price_data(stock_symbol: str, stock_market_time: StockMarketTime) -> str:
    stock = yf.Ticker(stock_symbol)
    start = stock_market_time.last_time_closed
    end = stock_market_time.next_time_open
    stock_data = stock.history(period="5d", interval="1m", prepost=True)

    stock_data = stock_data[(stock_data.index >= start) & (stock_data.index <= end)]
    stock_data.to_csv(f"temp/{stock_symbol}_data.csv")

    previous_close = stock_data.iloc[0]['Open']
    open_price = stock_data.iloc[-1]['Open']

    return (
        f"Previous Close (Yesterday): {previous_close}\n"
        f"Open Price (Today): {open_price}\n"
    )


def get_news_data(company_name: str, stock_symbol: str, stock_market_time: StockMarketTime) -> str:
    stock = yf.Ticker(stock_symbol)
    news = stock.news
    relevant_news = []
    urls = set()

    for news_item in tqdm(news):
        published_timestamp = news_item['providerPublishTime']
        published_time = datetime.datetime.fromtimestamp(published_timestamp, MARKET_TIME_ZONE)

        if not (stock_market_time.last_time_closed < published_time < stock_market_time.next_time_open):
            continue

        url = news_item.get('link')
        if not url:
            continue

        relevant_news.append(news_item)
        urls.add(url)

    logging.info(f"Number of relevant news items: {len(relevant_news)}")

    if not relevant_news:
        return (f"No relevant news found for {company_name} "
                f"between {stock_market_time.last_time_closed} and "
                f"{stock_market_time.next_time_open}.")

    text_by_link = asyncio.run(get_text_by_url(urls))
    news_data = ""

    for news_item in tqdm(relevant_news):
        link = news_item['link']
        text = text_by_link.get(link)
        if not text:
            continue

        published_timestamp = news_item['providerPublishTime']
        published_time = datetime.datetime.fromtimestamp(published_timestamp, MARKET_TIME_ZONE)
        summary = summarize_with_open_ai(text, link, company_name, stock_symbol)

        if not summary:
            continue

        news_data += (f"Headline: {news_item['title'].strip()}\n"
                      f"Date: {published_time}\n"
                      f"Summary: {summary.strip()}\n\n")

    return news_data

# # for testing purposes
# if __name__ == "__main__":
#     now = datetime.datetime.now(MARKET_TIME_ZONE)
#     mock_data_input_now = now.replace(hour=9, minute=0, second=0, microsecond=0)
#     r = create_content(mock_data_input_now=mock_data_input_now)
#     print(r)
