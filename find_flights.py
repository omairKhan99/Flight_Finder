import os
from datetime import datetime, timedelta
from amadeus import Client, ResponseError

AMADEUS_API_KEY = os.getenv('AMADEUS_API_KEY')
AMADEUS_API_SECRET = os.getenv('AMADEUS_API_SECRET')

ORIGIN_CITY = 'PHX'
DESTINATION_CITY = 'ISB'
DEPARTURE_DATE = '2025-10-31'
RETURN_DATE = '2025-11-30'
CURRENCY = 'USD'
HUB_AIRPORTS = [
    'JFK', 'LAX', 'DFW', 'ORD', 'SFO', 'IAD', 'IAH', 'SEA', 'EWR', 'ATL'
]

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

    amadeus = Client(
        client_id=AMADEUS_API_KEY,
        client_secret=AMADEUS_API_SECRET
    )

    print("\n--- Phase 1: Searching for all individual flight legs ---")
    leg1_flights = {hub: search_flights(amadeus, ORIGIN_CITY, hub, DEPARTURE_DATE) for hub in HUB_AIRPORTS}
    leg2_flights = {hub: search_flights(amadeus, hub, DESTINATION_CITY, DEPARTURE_DATE) for hub in HUB_AIRPORTS}
    leg3_flights = {hub: search_flights(amadeus, DESTINATION_CITY, hub, RETURN_DATE) for hub in HUB_AIRPORTS}
    leg4_flights = {hub: search_flights(amadeus, hub, ORIGIN_CITY, RETURN_DATE) for hub in HUB_AIRPORTS}

    print("\n--- Phase 2: Combining outbound and inbound journeys ---")
    outbound_journeys = []
    for hub in HUB_AIRPORTS:
        if leg1_flights.get(hub) and leg2_flights.get(hub):
            for flight1 in leg1_flights[hub]:
                for flight2 in leg2_flights[hub]:
                    leg1_arrival = datetime.fromisoformat(flight1['itineraries'][0]['segments'][-1]['arrival']['at'])
                    leg2_departure = datetime.fromisoformat(flight2['itineraries'][0]['segments'][0]['departure']['at'])
                    if leg2_departure > leg1_arrival + timedelta(minutes=90):
                        outbound_journeys.append({
                            'hub': hub,
                            'price': float(flight1['price']['grandTotal']) + float(flight2['price']['grandTotal']),
                            'details': f"{ORIGIN_CITY} -> {hub} -> {DESTINATION_CITY}"
                        })

    inbound_journeys = []
    for hub in HUB_AIRPORTS:
        if leg3_flights.get(hub) and leg4_flights.get(hub):
            for flight3 in leg3_flights[hub]:
                for flight4 in leg4_flights[hub]:
                    leg3_arrival = datetime.fromisoformat(flight3['itineraries'][0]['segments'][-1]['arrival']['at'])
                    leg4_departure = datetime.fromisoformat(flight4['itineraries'][0]['segments'][0]['departure']['at'])
                    if leg4_departure > leg3_arrival + timedelta(minutes=90):
                        inbound_journeys.append({
                            'hub': hub,
                            'price': float(flight3['price']['grandTotal']) + float(flight4['price']['grandTotal']),
                            'details': f"{DESTINATION_CITY} -> {hub} -> {ORIGIN_CITY}"
                        })

    if not outbound_journeys or not inbound_journeys:
        print("\nCould not find valid outbound or inbound journeys. Try different dates or hubs.")
        return

    print("\n--- Phase 3: Combining into full round trips and calculating total price ---")
    full_round_trips = []
    for outbound in outbound_journeys:
        for inbound in inbound_journeys:
            full_round_trips.append({
                'total_price': outbound['price'] + inbound['price'],
                'outbound_details': outbound['details'],
                'outbound_price': outbound['price'],
                'inbound_details': inbound['details'],
                'inbound_price': inbound['price']
            })

    if not full_round_trips:
        print("\nNo valid full round trips could be constructed.")
        return

    print("\n--- Here are the top 5 cheapest round trip options found! ---")
    sorted_trips = sorted(full_round_trips, key=lambda x: x['total_price'])

    for i, trip in enumerate(sorted_trips[:5]):
        print(f"\n--- Option #{i+1} ---")
        print(f"✈️  Total Round Trip Price: ${trip['total_price']:.2f} {CURRENCY}")
        print(f"  -> Outbound: ${trip['outbound_price']:.2f} | Route: {trip['outbound_details']}")
        print(f"  <- Inbound:  ${trip['inbound_price']:.2f} | Route: {trip['inbound_details']}")
        print("-" * 25)

if __name__ == "__main__":
    main()
