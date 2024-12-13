import pyowm as owm, pandas as pd, seaborn as sns, matplotlib.pyplot as plt, requests, datetime
#Access to basic information
API_KEY = 'a4893ddea477ecfd57c3f022101e3a9b'
owm = owm.OWM(API_KEY)
mgr = owm.weather_manager()

def country_code_search():
    print('Country code of the city.')
    city = input('Name of the city: ')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "sys" in data and "country" in data["sys"]:
            country_code = data["sys"]["country"]
            print(f"The country code for {city} is {country_code}")
        else:
            print(f"Could not retrieve country code for {city}.")
    else:
        print(f"City '{city}' not found. Please check the city name and try again.")

def weather_info(location):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        geo_data = response.json()
        if len(geo_data) == 0:
            print(f"City '{location}' not found. Please check the city name and try again.")
            return None
        try:
            forecast = mgr.forecast_at_place(location, '3h')
            weathers = forecast.forecast.weathers
            data_weather = {
                "time": [weather.reference_time('iso') for weather in weathers],
                "temperature": [weather.temperature('celsius')['temp'] for weather in weathers],
                "humidity": [weather.humidity for weather in weathers],
                "wind_speed": [weather.wind()['speed'] for weather in weathers]
            }
            df_w = pd.DataFrame(data_weather)
            df_w['time'] = pd.to_datetime(df_w['time'])
            df_w.set_index('time', inplace=True)
        except Exception as e:
            print(f"Error fetching weather data for {location}: {e}")
            return None
    else:
        print(f"Failed to retrieve location information for {location}. Status code: {response.status_code}")
        return None
    
    warnings = []
    current_temp = df_w.iloc[0]['temperature']
    current_humidity = df_w.iloc[0]['humidity']
    current_wind_speed = df_w.iloc[0]['wind_speed']
    
    if current_temp > 35: 
        warnings.append("Currently the temperature is high, please pay attention to prevent heatstroke!")
    if current_temp < 5: 
        warnings.append("Currently the temperature is low, Please take care to keep warm!")
    if current_humidity < 20: 
        warnings.append("Currently the humidity is low, so please take care of hydration!")
    if current_wind_speed > 15:
        warnings.append("Currently the wind speed is high, please avoid prolonged outdoor activities!")
    
    for warning in warnings:
        print(f"warning: {warning}")
    
    return df_w

#weather actions
def time_thw(df_w):
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_w, x='time', y='temperature', label='Temperature (°C)', color='red')
    sns.lineplot(data=df_w, x='time', y='humidity', label='Humidity (%)', color='blue')
    sns.lineplot(data=df_w, x='time', y='wind_speed', label='Wind Speed (m/s)', color='yellow')
    plt.title('Temperature and Humidity Over Time')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

def hum_win(df_w):
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df_w, x='humidity', y='wind_speed', color='purple')
    plt.title('Humidity vs Wind Speed')
    plt.xlabel('Humidity (%)')
    plt.ylabel('Wind Speed (m/s)')
    plt.show()

#air info
def air_info(location):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={API_KEY}"
    info = (requests.get(url)).json()
    lat = info[0]['lat']
    lon = info[0]['lon']
    data_air = (requests.get(f'http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={API_KEY}')).json()
    a = data_air['list'][0]  
    components = a['components']
    dt = a['dt']
    AQI_w = a['main']
    data_a = {
        "time": dt,  
        "pm2_5": components["pm2_5"],  
        "pm10": components["pm10"], 
        "co": components["co"], 
        "no2": components["no2"], 
        "so2": components["so2"],
        "o3": components["o3"], 
        "aqi": AQI_w["aqi"]  
    }
    warnings = []
    if components["pm2_5"] > 35:  
        warnings.append("PM2.5 concentration is too high, please take care of your health!")
    if components["pm10"] > 50:  
        warnings.append("PM10 concentration is too high, may affect the respiratory system!")
    if components["co"] > 10:  
        warnings.append("Carbon monoxide concentration is too high, take care of ventilation!")
    if components["no2"] > 40:  
        warnings.append("Nitrogen dioxide concentration is too high, may trigger respiratory discomfort!")
    if components["so2"] > 20:  
        warnings.append("Sulphur dioxide concentration is too high, may irritate the respiratory tract!")
    if components["o3"] > 100:  
        warnings.append("Ozone concentration is too high, avoid prolonged outdoor activities!")
    
    for warning in warnings:
        print(f"warning: {warning}")
    df_a = pd.DataFrame([data_a])
    return df_a
#air actions
def Pollutant_Concentrations(df_a):
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(df_a.columns[1:-1]), y=df_a.iloc[0, 1:-1], hue=list(df_a.columns[1:-1]), palette="coolwarm")
    plt.title('Pollutant Concentrations')
    plt.xlabel('Pollutants')
    plt.ylabel('Concentration (µg/m³ or µmol/m³)')
    plt.show()
print('\n\n\n\n\n\n\n')
n=0
while n==0:
    print(f"---------------------------------------------\n0: Country code search\n1: Meteorological search\n2: Quit")
    l1 = None
    try:
        Input1 = int(input("Your choice: "))  
        if 0 <= Input1 <= 2:  
            l1 = Input1
        else:
            print("Please input a valid number (0, 1, or 2).")
    except ValueError:
        print("Please input an integer.")
    if l1 is not None:
        if l1 == 0:
            print('---------------------------------------------')
            country_code_search()
        elif l1 == 1:
            print("---------------------------------------------\nCities of enquiry\nFor example: San Francisco, US\nNote: Use (City, CountryCode) format to ensure accurate results.")
            location = input(':')
            print("---------------------------------------------\n0: Overview\n1: Humidity and wind speed\n2: Pollution statistics\n3: Quit")
            
            try:
                l2 = int(input("Your choice: "))
                if l2 == 0:
                    time_thw(weather_info(location))
                elif l2 == 1:
                    hum_win(weather_info(location))
                elif l2 == 2:
                    Pollutant_Concentrations(air_info(location))
                elif l2 == 3:
                    continue
                else:
                    print("Please input a valid number (0 to 3).")
            except ValueError:
                print("Please input an integer.")
        elif l1 == 2:
            print("Exiting the program. Have a great day!")
            break
