# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import os
import datetime
from urllib.parse import quote
from playwright.sync_api import sync_playwright

# These values will be passed from GitHub Secrets

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# The URL of the product page to track
URL = 'https://www.gitana.lv/darza-tehnika/zaliena-roboti/zaliena-robots-segway-navimow-x330e?search_query=navimow+330'
RD_URL = 'https://www.rdveikals.lv/products/lv/1935/819719/sort/5/filter/0_0_0_0/Navimow-X330E-Robots-' + quote("zāles-pļāvējs.html")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_price():
    """Scrapes the website for the price."""
    try:
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_element = soup.find('span', id='our_price_display', class_='price') # Update this line!
        if price_element:
            return price_element.text.strip()
        else:
            return None
    except Exception as e:
        print(f"Error scraping price: {e}")
        return None


def get_priceRD():
    """Scrapes RD site for the price using Playwright (bypasses Cloudflare)."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(RD_URL, timeout=60000)
            page.wait_for_selector("span.price[itemprop=price]", timeout=15000)
            price_element = page.query_selector("span.price[itemprop=price]")
            if price_element:
                return price_element.inner_text().strip()
            else:
                print("Price element not found on RD page")
                return None
    except Exception as e:
        print(f"Error scraping RD price: {e}")
        return None


def send_telegram_message(message):
    """Sends a message to your Telegram chat."""
    # Note: There is a slash after 'bot' in the URL, as we confirmed earlier.
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    try:
        response = requests.post(url, data=payload)
        
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        # This will show you the error message from the API's response body
        print(f"Response Content: {err.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main logic
rd = get_priceRD()
current_price = get_price()

print(rd, current_price)
# match = re.search(r'[\d\s]+', current_price)
# match_rd = re.search(r'[\d\s]+', rd)
# if match:
#     # Get the matched part
#     number_part = match.group(0).strip()
#     # Clean up the space to get the final number
#     final_number = int(number_part.replace(' ', ''))

# if match_rd:
#     # Get the matched part
#     number_part_rd = match_rd.group(0).strip()
#     # Clean up the space to get the final number
#     final_number_rd = int(number_part_rd.replace(' ', ''))



# day_ = datetime.date.today().weekday() == 3
    

send_telegram_message(f"Gintara:{current_price}\nRD: {rd}")
