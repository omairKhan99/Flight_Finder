import os
import json
from datetime import datetime, timedelta
from amadeus import Client, ResponseError

AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY')
AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET')


ORIGIN_CITY = 'PHX'
DESTINATION_CITY = 'ISB'
SEARCH_DATE = '2025-10-31'
CURRENCY = 'USD'

# List of major US hubs to check for layovers.
# You can add or remove airports from this list.
HUB_AIRPORTS = [
    'JFK', # New York
    'LAX', # Los Angeles
    'DFW', # Dallas/Fort Worth
    'ORD', # Chicago O'Hare
    'SFO', # San Francisco
    'IAD', # Washington Dulles
    'IAH', # Houston
    'SEA', # Seattle
    'EWR', # Newark
    'ATL', # Atlanta
]


def search_flights(amadeus, origin, destination, date):
    """
    Searches for one-way flights for a given route and date.
    Returns a list of flight offers from the API response.
    """
    try:
        print(f"Searching for flights from {origin} to {destination} on {date}...")
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            currencyCode=CURRENCY,
            max=10 
        )
        return response.data
    except ResponseError as error:
        print(f"⚠️  API Error for {origin}->{destination}: {error}")
        return []

def main():
    """Main function to find and combine flights."""
    if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
        print("❌ ERROR: Make sure you have set AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables.")
        return

    amadeus = Client(
        client_id=AMADEUS_API_KEY,
        client_secret=AMADEUS_API_SECRET
    )

    print("\n--- Phase 1: Searching for individual flight legs ---")

    leg1_flights = {}
    for hub in HUB_AIRPORTS:
        flights = search_flights(amadeus, ORIGIN_CITY, hub, SEARCH_DATE)
        if flights:
            leg1_flights[hub] = flights

    leg2_flights = {}
    for hub in HUB_AIRPORTS:
        flights = search_flights(amadeus, hub, DESTINATION_CITY, SEARCH_DATE)
        if flights:
            leg2_flights[hub] = flights

    if not leg1_flights or not leg2_flights:
        print("\n❌ Could not find flights for one of the legs. Try different dates or hubs.")
        return
        
    print("\n--- Phase 2: Combining flight legs and calculating total price ---")
    combined_trips = []

    for hub in HUB_AIRPORTS:
        if hub in leg1_flights and hub in leg2_flights:
            for flight1 in leg1_flights[hub]:
                for flight2 in leg2_flights[hub]:
                    
                    leg1_price = float(flight1['price']['grandTotal'])
                    leg1_segments = flight1['itineraries'][0]['segments']
                    leg1_departure_time = datetime.fromisoformat(leg1_segments[0]['departure']['at'])
                    leg1_arrival_time = datetime.fromisoformat(leg1_segments[-1]['arrival']['at'])

                    leg2_price = float(flight2['price']['grandTotal'])
                    leg2_segments = flight2['itineraries'][0]['segments']
                    leg2_departure_time = datetime.fromisoformat(leg2_segments[0]['departure']['at'])
                    leg2_arrival_time = datetime.fromisoformat(leg2_segments[-1]['arrival']['at'])
 
                    layover_duration = leg2_departure_time - leg1_arrival_time
                    if layover_duration > timedelta(minutes=90): #The layover should be at least 90 minutes for international connections
                        
                        combined_trips.append({
                            'hub': hub,
                            'total_price': leg1_price + leg2_price,
                            'layover_duration': layover_duration,
                            'total_travel_time': leg2_arrival_time - leg1_departure_time,
                            'details': {
                                'leg1': f"{ORIGIN_CITY} -> {hub}",
                                'leg1_departure': leg1_departure_time.strftime('%I:%M %p'),
                                'leg1_arrival': leg1_arrival_time.strftime('%I:%M %p'),
                                'leg1_price': leg1_price,
                                'leg2': f"{hub} -> {DESTINATION_CITY}",
                                'leg2_departure': leg2_departure_time.strftime('%I:%M %p'),
                                'leg2_arrival': leg2_arrival_time.strftime('%I:%M %p'),
                                'leg2_price': leg2_price,
                            }
                        })

    print("\n--- Phase 3: Here are the best flight options found! ---")
    
    if not combined_trips:
        print("\n❌ No valid connecting flights found with the current hubs and date.")
        return

    sorted_trips = sorted(combined_trips, key=lambda x: x['total_price'])

    for i, trip in enumerate(sorted_trips[:5]):
        layover_hours = trip['layover_duration'].total_seconds() // 3600
        layover_minutes = (trip['layover_duration'].total_seconds() % 3600) // 60
        
        print(f"\n--- Option #{i+1} ---")
        print(f"✈️  Total Price: ${trip['total_price']:.2f} {CURRENCY}")
        print(f"📍 Route: {ORIGIN_CITY} -> {trip['hub']} -> {DESTINATION_CITY}")
        print(f"⌛ Layover in {trip['hub']}: {int(layover_hours)} hours {int(layover_minutes)} minutes")
        print(f"  - Leg 1 ({trip['details']['leg1']}): Departs {trip['details']['leg1_departure']}, Arrives {trip['details']['leg1_arrival']} (${trip['details']['leg1_price']})")
        print(f"  - Leg 2 ({trip['details']['leg2']}): Departs {trip['details']['leg2_departure']}, Arrives {trip['details']['leg2_arrival']} (${trip['details']['leg2_price']})")
        print("-" * 20)


if __name__ == "__main__":
    main()