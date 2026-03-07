import os
from typing import Optional
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from langchain.tools import tool
from tavily_with_conditional_edge import build_graph_one_tool, app_call, get_current_date_tool

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
model = os.getenv("MODEL", "gpt-5.2")   
amadeus_api_key = os.getenv("AMADEUS_API_KEY")
amadeus_secret_key = os.getenv("AMADEUS_SECRET_KEY")

amadeus = Client(
    client_id=amadeus_api_key,
    client_secret=amadeus_secret_key,
    hostname="test"
)

print("Amadeus API Client initialized successfully!")

@tool
def search_flight_tool(
    origin: str, 
    destination: str, 
    departure_date: str, 
    return_date: Optional[str] = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    currency: str = "INR",
    max_offers: int = 5
) -> str:
    """
        Search live flights prices and availability using the Amadeus API.
        Require:
        - origin: IATA code of the origin airport (e.g., "JFK")
        - destination: IATA code of the destination airport (e.g., "LHR")
        - departure_date: Departure date in YYYY-MM-DD format (e.g., "2024-12-01")
        Optional:
        - return_date: Return date in YYYY-MM-DD format (e.g., "2024-12-15")
        - adults: Number of adult passengers (default: 1)
        - travel_class: Travel class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST) (default: ECONOMY)
        - currency: Currency code for the prices (default: INR)
        - max_offers: Maximum number of flight offers to return (default: 5)
    """
    
    print(
        f"Debug: calling amadeus flight search"
        f" with origin={origin}, destination={destination}, departure_date={departure_date}, "
        f"return_date={return_date}, adults={adults}, travel_class={travel_class}"
    )

    flight_search_params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "travelClass": travel_class,
        "currency": currency,
        "maxOffers": max_offers
    }

    if return_date:
        flight_search_params["returnDate"] = return_date

    try:
        response = amadeus.shopping.flight_offers_search.get(**flight_search_params)
        if not response.data:
            return "No flight offers found for the given parameters."
        
        results = []
        for offer in response.data[:max_offers]:
            price = offer["price"]["total"]
            airline = offer["validatingAirlineCodes"][0]
            itineraries = offer["itineraries"][0]
            segments = itineraries["segments"]
            first_leg = segments[0]
            last_leg = segments[-1]
            dept_time = first_leg["departure"]["at"][:16].replace("T", " ")
            arr_time = last_leg["arrival"]["at"][:16].replace("T", " ")
            duration = itineraries["duration"].replace("PT", " ")
            results.append(f"{airline} | {dept_time} -> {arr_time} | {duration} | {price} {currency}")
            
        return "found flight options: \n" + "\n".join(results)
        
    except ResponseError as error:
        print(f"Error searching for flights: {error}")
        return "Error searching for flights."
    

tools_list = [get_current_date_tool, search_flight_tool]

app_flight_search = build_graph_one_tool(tools_list)

prompt = input("Enter your flight search query please! \n ")

history, output = app_call(app_flight_search, prompt)

print("===========Final Output========== \n", output)