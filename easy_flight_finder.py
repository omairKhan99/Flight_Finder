import os
from datetime import datetime, timedelta
from amadeus import Client, ResponseError
import results_renderer

AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY')
AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET')

ORIGIN_CITY = 'PHX'
DESTINATION_CITY = 'ISB'
DEPARTURE_DATE = '2025-10-25'
RETURN_DATE = '2025-11-15'
CURRENCY = 'USD'

def discover_hubs(amadeus, origin, destination, date):
    print(f"Discovering hubs for {origin} -> {destination}...")
    hubs = set()
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1,
            max=25 
        )
        for offer in response.data:
            for itinerary in offer['itineraries']:
                if len(itinerary['segments']) > 1:
                    for segment in itinerary['segments'][:-1]:
                        hubs.add(segment['arrival']['iataCode'])
    except ResponseError as error:
        print(f"Could not discover hubs for {origin}->{destination}: {error}")
    return list(hubs)

def search_flights(amadeus, origin, destination, date):
    try:
        print(f"Searching: {origin} -> {destination} on {date}")
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
        print(f"API Error for {origin}->{destination}: {error}")
        return []

def main():
    if not AMADEUS_API_KEY or not AMADEUS_API_SECRET:
        print("ERROR: Make sure AMADEUS_API_KEY and AMADEUS_API_SECRET environment variables are set.")
        return

    amadeus = Client(client_id=AMADEUS_API_KEY, client_secret=AMADEUS_API_SECRET)

    print("\n--- Phase 1: Automatically Discovering Hub Airports ---")
    outbound_hubs = discover_hubs(amadeus, ORIGIN_CITY, DESTINATION_CITY, DEPARTURE_DATE)
    inbound_hubs = discover_hubs(amadeus, DESTINATION_CITY, ORIGIN_CITY, RETURN_DATE)
    all_hubs = list(set(outbound_hubs + inbound_hubs))
    if not all_hubs:
        print("\nCould not discover any connecting hubs. The route may be direct or not have available data.")
        return
    print(f"Discovered Hubs: {', '.join(all_hubs)}")

    print("\n--- Phase 2: Searching for all individual flight legs ---")
    leg1_flights = {hub: search_flights(amadeus, ORIGIN_CITY, hub, DEPARTURE_DATE) for hub in all_hubs}
    leg2_flights = {hub: search_flights(amadeus, hub, DESTINATION_CITY, DEPARTURE_DATE) for hub in all_hubs}
    leg3_flights = {hub: search_flights(amadeus, DESTINATION_CITY, hub, RETURN_DATE) for hub in all_hubs}
    leg4_flights = {hub: search_flights(amadeus, hub, ORIGIN_CITY, RETURN_DATE) for hub in all_hubs}

    print("\n--- Phase 3: Combining journeys ---")
    outbound_journeys = []
    for hub in all_hubs:
        if leg1_flights.get(hub) and leg2_flights.get(hub):
            for f1 in leg1_flights[hub]:
                for f2 in leg2_flights[hub]:
                    if datetime.fromisoformat(f2['itineraries'][0]['segments'][0]['departure']['at']) > datetime.fromisoformat(f1['itineraries'][0]['segments'][-1]['arrival']['at']) + timedelta(minutes=90):
                        outbound_journeys.append({'hub': hub, 'price': float(f1['price']['grandTotal']) + float(f2['price']['grandTotal']), 'details': f"{ORIGIN_CITY} -> {hub} -> {DESTINATION_CITY}"})

    inbound_journeys = []
    for hub in all_hubs:
        if leg3_flights.get(hub) and leg4_flights.get(hub):
            for f3 in leg3_flights[hub]:
                for f4 in leg4_flights[hub]:
                    if datetime.fromisoformat(f4['itineraries'][0]['segments'][0]['departure']['at']) > datetime.fromisoformat(f3['itineraries'][0]['segments'][-1]['arrival']['at']) + timedelta(minutes=90):
                        inbound_journeys.append({'hub': hub, 'price': float(f3['price']['grandTotal']) + float(f4['price']['grandTotal']), 'details': f"{DESTINATION_CITY} -> {hub} -> {ORIGIN_CITY}"})

    if not outbound_journeys or not inbound_journeys:
        print("\nCould not find valid combined journeys.")
        return

    print("\n--- Phase 4: Combining into full round trips ---")
    full_round_trips = []
    for outbound in outbound_journeys:
        for inbound in inbound_journeys:
            full_round_trips.append({'total_price': outbound['price'] + inbound['price'], 'outbound_details': outbound['details'], 'outbound_price': outbound['price'], 'inbound_details': inbound['details'], 'inbound_price': inbound['price']})

    if not full_round_trips:
        print("\nNo valid full round trips could be constructed.")
        return

    sorted_trips = sorted(full_round_trips, key=lambda x: x['total_price'])
    
    results_renderer.generate_html_report(sorted_trips[:25], ORIGIN_CITY, DESTINATION_CITY, DEPARTURE_DATE, RETURN_DATE)

if __name__ == "__main__":
    main()
