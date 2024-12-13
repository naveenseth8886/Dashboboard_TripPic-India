from flask import Flask, request, render_template, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/nextpage.html")
def source():
    return render_template("source_data.html")

# Route to handle form submission
global start_date
global end_date
global departure
@app.route("/submit", methods=["POST"])
def submit():
    # Fetch data from the form
    departure = request.form.get("departure")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    
    # Pass the data to the dashboard template
    return render_template("dashboard.html", departure=departure, start_date=start_date, end_date=end_date)

# Route to handle city data retrieval
def fetch_weather_forecast(start_date, end_date, city):
    API_KEY = "4af276f0c7f4969789e272dae0a06f5e"  # OpenWeatherMap API key
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",  # Celsius
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Error fetching weather data:", response.json())
            return []
        
        data = response.json()
        forecast_list = data.get("list", [])
        
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        filtered_data = []
        for forecast in forecast_list:
            forecast_datetime = datetime.utcfromtimestamp(forecast["dt"])
            forecast_date = forecast_datetime.date()
            if start_date <= forecast_date <= end_date:
                filtered_data.append({
                    "date": forecast_date.strftime("%Y-%m-%d"),
                    "time": forecast["dt_txt"],
                    "temperature": forecast["main"]["temp"],
                    "weather": forecast["weather"][0]["description"],
                })
        
        return filtered_data
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Fetch news from NewsAPI
def fetch_news_from_newsapi(city):
    try:
        NEWS_API_KEY = "4ccb418765c04e3e98f32da30f62f60f"  # NewsAPI key
        url = f"https://newsapi.org/v2/everything?q={city}&apiKey={NEWS_API_KEY}&pageSize=5"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching news for {city}: {response.status_code}")
            return []

        data = response.json()
        if "articles" not in data:
            print(f"No articles found for {city}")
            return []
        
        articles = data["articles"]
        news_data = []
        for article in articles:
            news_data.append({
                "title": article["title"],
                "description": article["description"],
                "url": article.get("url", "#")
            })
        
        return news_data
    
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")
        return []

# Fetch flight data from AviationStack API
def fetch_flight_data(departure, start_date, end_date):
    API_KEY = "30560441b07f61f65917dbc1a0fb3079"  # Your AviationStack API key
    try:
        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": API_KEY,
            "departure_iata": departure,  # Departure airport code (e.g., JFK, LHR)
            "date_from": start_date,
            "date_to": end_date,
            "limit": 5  # Limit to 5 flights (can be adjusted)
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error fetching flight data: {response.status_code}")
            return []

        data = response.json()
        print(data)
        if "data" not in data:
            print(f"No flight data found for {departure}")
            return []

        flights = data["data"]
        flight_data = []
        for flight in flights:
            flight_data.append({
                "flight_name": flight.get("flight", {}).get("airline", {}).get("name", "N/A"),
                "price": flight.get("price", "N/A"),
                "duration": flight.get("duration", "N/A")
            })

        return flight_data
    
    except Exception as e:
        print(f"An error occurred while fetching flight data: {e}")
        return []

@app.route("/get_city_data")
def get_city_data():
    city = request.args.get("city")  # Fetch the city name from the query parameters

    if not city:
        return jsonify({"error": "City parameter is missing"}), 400
    
    # Fetch the weather data for the selected city
    weather_data = fetch_weather_forecast("2024-12-16", "2024-12-20", city)

    # Fetch the news data for the selected city
    news_data = fetch_news_from_newsapi(city)

    # Fetch flight data for the selected departure city and dates
    departure = request.args.get("departure")  # This should be passed from the frontend
    flight_data = fetch_flight_data(departure, "2024-12-16", "2024-12-20")

    # Prepare the response data
    response_data = {
        "weather": weather_data,
        "news": news_data,  # Include fetched news
        "flights": flight_data  # Include fetched flight data
    }

    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)
