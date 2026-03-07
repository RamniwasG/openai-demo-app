import os
import uuid
import gradio as gr
from typing import Optional
from dotenv import load_dotenv
from amadeus import Client, ResponseError
from langchain.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from tavily_with_conditional_edge import build_graph_one_tool, app_call, get_current_date_tool, tavily_search_tool

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
model = os.getenv("MODEL", "gpt-5.2")   
amadeus_api_key = os.getenv("AMADEUS_API_KEY")
amadeus_secret_key = os.getenv("AMADEUS_SECRET_KEY")

amadeus_client = Client(
    client_id=amadeus_api_key,
    client_secret=amadeus_secret_key,
    hostname="test"
)
print("Amadeus Client initialized successfully!")

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
        f"Debug: calling amadeus flight search -"
        f" with origin={origin}, destination={destination}"
        f" depart_at {departure_date}, return_date={return_date}"
        f" adults={adults}, travel_class={travel_class}"
    )

    flight_search_params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "adults": adults,
        "travelClass": travel_class,
        "currencyCode": currency,
        "max": max_offers
    }

    if return_date:
        flight_search_params["returnDate"] = return_date

    try:
        response = amadeus_client.shopping.flight_offers_search.get(**flight_search_params)
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

        print("found flight options: \n" + "\n".join(results))    
        return "found flight options: \n" + "\n".join(results)
        
    except ResponseError as error:
        print(f"Error searching for flights: {error}")
        return "Error searching for flights."
    

# tools_list = [get_current_date_tool, search_flight_tool]

# app_flight_search = build_graph_one_tool(tools_list)

# # prompt = 'I want to go to paris from toranto for the first week of June. can you please search flight for 2 adults'
# prompt = input("Enter your flight search query: \n ")

# history, output = app_call(app_flight_search, prompt)

# print("===========Flight Final Output========== \n", output)


# Flight search tool
@tool
def search_hotel_tools(city_code: str, check_in_date: str, check_out_date: str, adults: int = 1, rooms: int = 1) -> str:
    """
    Search hotels in a city for given check-in and check-out dates, number of adults and rooms.
    Parameters:
        - city_code: IATA code of the city (e.g., "NYC")
        - check_in_date: Check-in date in YYYY-MM-DD format (e.g., "2024-12-01")
        - check_out_date: Check-out date in YYYY-MM-DD format (e.g., "2024-12-05")
        - adults: Number of adult guests (default: 1)
        - rooms: Number of rooms required (default: 1)
    """

    print(
        f"Debug: calling hotel search -"
        f" with city_code={city_code}, check_in_date={check_in_date}, check_out_date={check_out_date}"
        f" adults={adults}, rooms={rooms}"
    )

    try:
        hotel_search_response = amadeus_client.reference_data.locations.hotels.by_city.get(
            cityCode=city_code, radius=50, radiusUnit="KM"
        )

        if not hotel_search_response.data or len(hotel_search_response.data) == 0:
            return f"No hotels found in {city_code}."
        
        hotelIds = [hotel["hotelId"] for hotel in hotel_search_response.data[:5]]  # Get top 5 hotels
        print(f"Debug: found hotel IDs - {hotelIds}")

        hotel_offer_response = amadeus_client.shopping.hotel_offers_search.get(
            hotelIds=", ".join(hotelIds),
            checkInDate=check_in_date, 
            checkOutDate=check_out_date, 
            adults=adults,
            rooms=rooms,
            bestRateOnly=True
        )

        if hotel_offer_response.data and len(hotel_offer_response.data) > 0:
            results = []
            for offer in hotel_offer_response.data[:5]:  # Get top 5 offers
                hotel_name = offer["hotel"]["name"]
                price = offer["offers"][0]["price"]["total"]
                currency = offer["offers"][0]["price"]["currency"]
                results.append(f"{hotel_name} | {price} {currency}")
            
            print("Found hotel options: \n" + "\n".join(results))
            return "Found hotel options: \n" + "\n".join(results)
        else:
            return f"No hotel offers found for the given parameters in {city_code}."
    
    except ResponseError as error:
        print(f"Error searching for hotels: {error.response.body}")
        return "Error searching for hotels."


# tools_list_full = [get_current_date_tool, search_flight_tool, search_hotel_tools]

# app_hotel_search = build_graph_one_tool(tools_list_full)

# prompt_hotel = "I want to go to newyork on 2026-04-01. please find hotels in newyork(city_code=NYC) for 2 adults and 1 room. if can't find then look for nearest city hotels and also provide the current date."

# hotel_history, hotels_output = app_call(app_hotel_search, prompt_hotel)

# print("===========Hotels Final Output========== \n", hotels_output)



# combining all the tools together in one app

travel_agent_tools = [tavily_search_tool, search_flight_tool, search_hotel_tools]

travel_agent_app = build_graph_one_tool(travel_agent_tools)

prompt_hotel = "I want the latest news about newyork. I'm planning to visit between 2026-04-01 to 2026-04-08. please find some flight & hotels in newyork(city_code=NYC) for 2 adults and 1 room. if can't find then look for nearest city hotels and also provide the current date."

ta_history, ta_output = app_call(travel_agent_app, prompt_hotel)

print("===========Travel Agent Final Output========== \n", ta_output)


def travel_agent_chat(user_input: str, history: None):
    tools_used = []
    stream = travel_agent_app.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config = { 
            "recursion_limit": 15, 
            "configurable": { "thread_id": str(uuid.uuid4()) }
        }
    )
    
    # 1. stream in tool calls and model tokens
    for chunk in stream:
        node = next(iter(chunk.items()))
        if isinstance(node, dict) and "messages" in node:
            for msg in node["messages"]:
                if isinstance(msg, ToolMessage):
                    if msg.name not in tools_used:
                        tools_used.append(msg.name)
                    yield(f"\n\n Tool : {msg.name} \n content : {msg.content} \n\n")
                    return
                else:
                    yield msg.content
                    return

    # 2. after streaming is done, return the final output and tools used
    if tools_used:
        yield f"\n\n Tools used in this session: {', '.join(tools_used)} \n\n"

    
travel_chatbot_interface = gr.ChatInterface(
    fn=travel_agent_chat,
    chatbot=gr.Chatbot(
        height=320,
        label="Travel Agent Chatbot",
        show_label=True,
        # show_copy_button=True,
        # bubble_full_width=False,
        # render_markdown=True
    ),
    textbox = gr.Textbox(
        label="Enter your travel query here",
        show_label=True,
        placeholder="Plan your trip, Ask about attractions, Search flights and hotels, Get travel advice... ",
    ),
    title = "LangGraph AI Travel Agent",
    description = "This is an AI-powered travel agent that can help you plan your trips, search for flights and hotels, and provide travel advice. It uses the Amadeus API for live flight and hotel data, and Tavily for real-time information retrieval.",
    examples = [
        ["what are top three attractions in paris?"],
        ["Find flights from NYC to LON departing on 2024-12-01 for 2 adults in economy class."],
        ["Search for hotels in Tokyo (TYO) from 2024-11-01 to 2024-11-05 for 1 adult and 1 room."]
    ],
    cache_examples = False
)

travel_chatbot_interface.launch()

