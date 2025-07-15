import webbrowser
import os

def generate_html_report(trips_data, origin, destination, departure_date, return_date):
    if not trips_data:
        print("No flight data to generate a report.")
        return

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flight Search Results</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{
                font-family: 'Inter', sans-serif;
            }}
        </style>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    </head>
    <body class="bg-slate-100">
        <div class="container mx-auto p-4 sm:p-6 lg:p-8">
            <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
                <h1 class="text-3xl font-bold text-slate-800">Flight Search Results</h1>
                <p class="text-lg text-slate-600 mt-2">
                    Showing the best options for <span class="font-semibold text-indigo-600">{origin} to {destination}</span>
                </p>
                <p class="text-md text-slate-500">
                    Departing: {departure_date} | Returning: {return_date}
                </p>
            </div>
            
            <div class="space-y-6">
    """

    for i, trip in enumerate(trips_data):
        html_content += f"""
                <div class="bg-white rounded-xl shadow-md overflow-hidden transition-all hover:shadow-xl">
                    <div class="p-6">
                        <div class="flex justify-between items-center">
                            <p class="text-sm font-semibold text-indigo-600 bg-indigo-100 rounded-full px-3 py-1">Option #{i+1}</p>
                            <p class="text-3xl font-bold text-slate-800">${trip['total_price']:.2f}</p>
                        </div>
                        <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-slate-50 p-4 rounded-lg">
                                <p class="font-bold text-slate-700">Outbound</p>
                                <p class="text-slate-600">{trip['outbound_details']}</p>
                                <p class="text-slate-800 font-semibold mt-1">${trip['outbound_price']:.2f}</p>
                            </div>
                            <div class="bg-slate-50 p-4 rounded-lg">
                                <p class="font-bold text-slate-700">Inbound</p>
                                <p class="text-slate-600">{trip['inbound_details']}</p>
                                <p class="text-slate-800 font-semibold mt-1">${trip['inbound_price']:.2f}</p>
                            </div>
                        </div>
                    </div>
                </div>
        """

    html_content += """
            </div>
        </div>
    </body>
    </html>
    """

    file_path = "flight_results.html"
    with open(file_path, "w") as f:
        f.write(html_content)
    
    print(f"\nResults have been saved to {file_path}")
    print("Opening results in your web browser...")

    webbrowser.open('file://' + os.path.realpath(file_path))

