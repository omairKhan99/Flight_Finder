# Automated Flight Deal Finder

This is a personal project I created to solve a real-world problem: finding the most affordable flight options for a complex, long-haul trip.

## The Problem

I’ll be traveling from Phoenix, AZ (PHX) to Islamabad, Pakistan (ISB) soon. Flights on this route almost always require at least two stops. The challenge is that the best price isn't always found by booking a single ticket from PHX to ISB.

Sometimes it’s cheaper to book two separate tickets:

- A domestic flight from Phoenix to a major international hub (like JFK, LAX, DFW, etc.)
- An international flight from that hub to Islamabad

Manually searching for all combinations across different hubs and dates is incredibly tedious. I wanted to automate this entire process with a script.

## The Solution

This Python script automates the search for these "two-leg" journeys. It uses the official Amadeus for Developers Self-Service API, which provides real-time flight data used by many major travel companies.

### How it works

1. Searches for one-way flights from the origin city (e.g., PHX) to a list of predefined major hub airports.
2. Searches for one-way flights from those same hubs to the final destination (e.g., ISB).
3. Combines the two legs, calculating the total price and ensuring there is a reasonable layover time.
4. Sorts all valid combined trips by total price and displays the top 5 cheapest options.

## How to Use This Script

### Prerequisites

- Python 3.6 or newer
- pip (Python's package installer)

### 1. Clone the Repository

```bash
git clone <https://github.com/omairKhan99/Flight_Finder.git
```

### 2. Install Dependencies

```bash
pip install amadeus
```

### 3. Get Your Free API Keys

```bash
Go to Amadeus for Developers and create a free account.
From your dashboard, create a new app to get your API Key and API Secret.
Note: It can take up to 30 minutes for newly generated keys to become active.
```

### 4. Set Environment Variables

On Windows (PowerShell)
```bash
$env:AMADEUS_API_KEY="YOUR_API_KEY_HERE"
$env:AMADEUS_API_SECRET="YOUR_API_SECRET_HERE"
```

On macOS / Linux
```bash
export AMADEUS_API_KEY="YOUR_API_KEY_HERE"
export AMADEUS_API_SECRET="YOUR_API_SECRET_HERE"
```

### 5. Configure Your Search
Open the find_flights.py file and edit the configuration section:
```bash
# --- Your Flight Search Parameters ---
ORIGIN_CITY = 'PHX'
DESTINATION_CITY = 'ISB'
SEARCH_DATE = '2025-10-25'  # Use YYYY-MM-DD format
CURRENCY = 'USD'
HUB_AIRPORTS = [
    'JFK', 'LAX', 'DFW', 'ORD', 'SFO',  # etc.
]
```

### 6. Run the Script

```bash
python find_flights.py
```






