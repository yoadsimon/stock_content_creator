import os
import logging
import time

from playwright.async_api import async_playwright

async def open_finance_yahoo(p):
    base_url = "https://finance.yahoo.com/"
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(base_url)
    await page.wait_for_timeout(10000)
    try:
        time.sleep(0.2)
        await page.click("button#scroll-down-btn")
        await page.click("button.btn.secondary.reject-all")
    except Exception as e:
        print(f"No consent buttons found or error clicking: {e}")
    return browser, page

async def get_text_from_url(url, page):
    try:
        await page.goto(url)
        await page.wait_for_timeout(10000)
        body_handle = await page.query_selector("body")
        if body_handle:
            text_raw = await page.evaluate("document.body.innerText")
        else:
            text_raw = "Error: Body element is not present on the page."
        return text_raw
    except Exception as e:
        print(f"Error fetching text from URL {url}: {e}")
        return None

async def get_text_by_url(urls):
    text_by_link = {}
    time.sleep(0.2)
    async with async_playwright() as p:
        browser, page = await open_finance_yahoo(p)
        if not browser or not page:
            print("Failed to open browser or page.")
            return text_by_link
        try:
            for url in urls:
                text = await get_text_from_url(url, page)
                text_by_link[url] = text
            return text_by_link
        finally:
            await browser.close()


def save_to_temp_file(text, name):
    if not os.path.exists('temp'):
        os.makedirs('temp')
    with open(f'temp/{name}.txt', 'w', encoding='utf-8') as file:
        file.write(text)
    pass


def read_temp_file(file_name):
    if not file_name:
        return None
    if 'temp' not in file_name:
        file_path = f"temp/{file_name}.txt"
    else:
        file_path = file_name

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content

    return None


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )