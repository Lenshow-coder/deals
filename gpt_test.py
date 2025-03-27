import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from functions import extract_hotel_details
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')

async def process_hotel(hotel, page, today):
    try:
        name = await hotel.locator('.hotel-name').inner_text()
        city = await hotel.locator('.hotel-city').inner_text()
        price_str = await hotel.locator('.price').inner_text()
        price = int(price_str.replace('$', '').replace(',', ''))
        if price > 2000:
            return None
        checkin = await hotel.locator('.checkin').inner_text()
        checkout = await hotel.locator('.checkout').inner_text()
        rating_img = hotel.locator('.vacv-trip-advisor__rating img')

        if await rating_img.count() > 0:
            alt = await rating_img.get_attribute('alt')
            rating = alt.split()[2]
        else:
            rating = 'N/A'

        await hotel.get_by_role("button", name="See hotel details").click()
        await page.wait_for_selector("iframe[title=\"hotel details\"]", state="visible")
        await asyncio.sleep(1)
        frame = await page.frame_locator("iframe[title=\"hotel details\"]").content_frame()
        headers = await frame.locator("heading").all_text_contents()
        plan = 'All Inclusive' if any('All Inclusive' in item for item in headers) else 'European'

        details = await frame.locator("section").filter(has_text="Check-in:").all_text_contents()
        check_in, check_out, rooms, restaurants, bars = extract_hotel_details(details)

        star_rating = await frame.locator(".star-rating div:first-child").get_attribute("class").split()[-1][-1]

        return [name, city, price, checkin, checkout, rating, plan, star_rating, check_in, check_out, rooms, restaurants, bars]

    except Exception as e:
        print(f"Error processing hotel: {e}")
        return None

async def process_destination(destination, page, today):
    id_value = await destination.get_attribute('id')
    value = id_value[-3:]
    print(f"Processing option: {value}")

    await page.goto(f"https://vacations.aircanada.com/en/all-deals/last-minute-deals?tripMonth=2025-03&leaveFrom=YYZ&goTo={value}&duration=5&vacationType=PACKAGE", wait_until='networkidle')
    
    hotels = await page.locator('.hotel-item').all()
    count = await page.locator('.hotel-item').count()
    print(f"{count} hotel items found for option {value}.")

    tasks = [process_hotel(hotel, page, today) for hotel in hotels]
    hotel_data = await asyncio.gather(*tasks)

    return hotel_data

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Use headless=True for better performance
        page = await browser.new_page()

        await page.goto("https://vacations.aircanada.com/en/all-deals/last-minute-deals?tripMonth=2025-03&leaveFrom=YYZ&goTo=CUN&duration=5&vacationType=PACKAGE")

        destinations = await page.locator('//*[@id="dropdown-button-travelTo"]/following-sibling::ul/li').all()

        # Define the columns for the CSV file
        columns = ['name', 'city', 'price', 'checkin', 'checkout', 'rating', 'plan', 'star_rating', 'check_in', 'check_out', 'rooms', 'restaurants', 'bars']

        # Open the CSV file in append mode and write the header
        hotel_data_list = []

        for destination in destinations:
            hotel_data = await process_destination(destination, page, today)
            hotel_data_list.extend(hotel_data)

        # Create a DataFrame from the hotel data and write to CSV
        df = pd.DataFrame(hotel_data_list, columns=columns)
        df.to_csv(f'deals_{today}.csv', mode='w', index=False, header=True, encoding='utf-8')

        await browser.close()

asyncio.run(main())
