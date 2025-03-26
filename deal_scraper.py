from playwright.sync_api import sync_playwright
import time
import pandas as pd
from functions import extract_hotel_details
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False) # Use slow_mo=100 to slow down the browser
    page = browser.new_page()

    page.goto("https://vacations.aircanada.com/en/all-deals/last-minute-deals?tripMonth=2025-03&leaveFrom=YYZ&goTo=CUN&duration=5&vacationType=PACKAGE")

    # Locate all the options in the dropdown
    destinations = page.locator('//*[@id="dropdown-button-travelTo"]/following-sibling::ul/li').all()

   # Define the columns for the CSV file
    columns = ['name', 'city', 'price', 'checkin', 'checkout', 'rating', 'plan', 'star_rating', 'check_in', 'check_out', 'rooms', 'restaurants', 'bars']

    # Open the CSV file in append mode and write the header
    with open('deals.csv', 'w', newline='', encoding='utf-8') as f:
        pd.DataFrame(columns=columns).to_csv(f, index=False, header=True)

    for destination in destinations:
        value = destination.get_attribute('id')[-3:]
        print(f"Processing option: {value}")

        # Update the URL based on the selected option
        page.goto(f"https://vacations.aircanada.com/en/all-deals/last-minute-deals?tripMonth=2025-03&leaveFrom=YYZ&goTo={value}&duration=5&vacationType=PACKAGE", wait_until='networkidle')
        
        hotels = page.locator(' .hotel-item').all()
        count = page.locator('.hotel-item').count()
        print(f"{count} hotel items found for option {value}.")

        for hotel in hotels:
            name = hotel.locator('.hotel-name').inner_text()
            city = hotel.locator('.hotel-city').inner_text()
            price_str = hotel.locator('.price').inner_text()
            price = int(price_str.replace('$', '').replace(',', ''))
            if price > 2000:
                break
            checkin = hotel.locator('.checkin').inner_text()
            checkout = hotel.locator('.checkout').inner_text()
            rating_img = hotel.locator('.vacv-trip-advisor__rating img')

            if rating_img.count() > 0:
                alt = rating_img.get_attribute('alt')
                rating = alt.split()[2]
            else:
                rating = 'N/A'

            hotel.get_by_role("button", name="See hotel details").click()
            page.wait_for_selector("iframe[title=\"hotel details\"]", state="visible")
            time.sleep(1)
            headers = page.locator("iframe[title=\"hotel details\"]").content_frame.get_by_role("heading").all_text_contents()
            plan = 'All Inclusive' if any('All Inclusive' in item for item in headers) else 'European'

            details = page.locator("iframe[title=\"hotel details\"]").content_frame.locator("section").filter(has_text="Check-in:").all_text_contents()
            check_in, check_out, rooms, restaurants, bars = extract_hotel_details(details)
            
            # page.locator("iframe[title=\"hotel details\"]").content_frame.locator(".stars").click()
            star_rating = page.locator("iframe[title=\"hotel details\"]").content_frame.locator(".star-rating div:first-child").get_attribute("class").split()[-1][-1]

            new_row = pd.DataFrame([[name, city, price, checkin, checkout, rating, plan, star_rating, check_in, check_out, rooms, restaurants, bars]],
                                    columns=['name', 'city', 'price', 'checkin', 'checkout', 'rating', 'plan', 'star_rating', 'check_in', 'check_out', 'rooms', 'restaurants', 'bars'])
                        
            # Append the new row to the CSV file
            with open(f'deals_{today}.csv', 'a', newline='', encoding='utf-8') as f:
                new_row.to_csv(f, index=False, header=False)

            page.mouse.click(1,1)

    browser.close()