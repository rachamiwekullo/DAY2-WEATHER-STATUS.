# Weather Status API

A small Python script that retrieves current weather information from the
[OpenWeather API](https://openweathermap.org/current) for Eldoret and Kampala.
It prints the temperature, weather description, and humidity, and reports
common errors such as an invalid API key or an unknown city.

## Requirements

- Python 3
- An OpenWeather API key

Install the Python packages:

```bash
python -m pip install requests python-dotenv
```

## Configure the API key

Create a `.env` file in the project root and add your key:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

Keep `.env` private; it is excluded from Git.

## Run

From the project root:

```bash
python "WEEK 1/day2_weather.py"
```
