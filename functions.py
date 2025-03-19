import re
import time

def extract_hotel_details(details):
    details = ' '.join([s.strip() for s in details])
    details = re.sub(r'\s+', ' ', details).strip()
    details = re.split(r'(?=[A-Z])', details)[1:]
    details = [item.split(':', 1) for item in details]
    
    time.sleep(1)

    try:
        check_in = [item[1].strip() for item in details if 'Check-in' in item[0]][0]
        check_out = [item[1].strip() for item in details if 'Check-out' in item[0]][0]
        rooms = [item[1].strip() for item in details if 'rooms' in item[0]][0]
        restaurants = [item[1].strip() for item in details if 'restaurants' in item[0]][0]
        bars = [item[1].strip() for item in details if 'bars' in item[0]][0]
    except:
        check_in = 'N/A'
        check_out = 'N/A'
        rooms = 'N/A'
        restaurants = 'N/A'
        bars = 'N/A'
    
    return check_in, check_out, rooms, restaurants, bars
