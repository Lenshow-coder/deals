from playwright.sync_api import sync_playwright
import time
import pandas as pd
from functions import extract_hotel_details

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) # Use slow_mo=100 to slow down the browser
    page = browser.new_page()

    df_hotels = pd.DataFrame()

    page.goto("https://vacations.aircanada.com/en/all-deals/last-minute-deals?tripMonth=2025-03&leaveFrom=YYZ&goTo=CUN&duration=5&vacationType=PACKAGE", wait_until='networkidle')

    hotels = page.locator(' .hotel-item').all()
    count = page.locator('.hotel-item').count()
    print(f"{count} hotel items found for option.")

    for hotel in hotels:
        hotel.get_by_role("button", name="See hotel details").click()
        page.wait_for_selector("iframe[title=\"hotel details\"]", state="visible")
        time.sleep(1)
        headers = page.locator("iframe[title=\"hotel details\"]").content_frame.get_by_role("heading").all_text_contents()
        plan = 'All Inclusive' if any('All Inclusive' in item for item in headers) else 'European'
        print(plan)

        details = page.locator("iframe[title=\"hotel details\"]").content_frame.locator("section").filter(has_text="Check-in:").all_text_contents()
        check_in, check_out, rooms, restaurants, bars = extract_hotel_details(details)
        print(check_in, check_out, rooms, restaurants, bars)
        
        # page.locator("iframe[title=\"hotel details\"]").content_frame.locator(".stars").click()
        star_rating = page.locator("iframe[title=\"hotel details\"]").content_frame.locator(".star-rating div:first-child").get_attribute("class").split()[-1][-1]
        print(star_rating)

        page.mouse.click(1,1)

        
    browser.close()