# Weather Status API

A small Python weather demo. It requests current conditions for Eldoret and Kampala from the OpenWeather API and displays temperature, weather description, and humidity.

## What It Does

- Fetches current weather for Eldoret and Kampala
- Displays temperature, conditions, and humidity
- Handles common API responses, including invalid API keys, unknown cities, and request limits

## Setup

Requires Python 3 and an OpenWeather API key.

Install the dependencies:

```bash
python -m pip install requests python-dotenv
```

Create a `.env` file in the project root and add your key:

```env
OPENWEATHER_API_KEY=your_api_key_here
```

Keep `.env` private; it is excluded from Git.

## Usage

From the project root, run:

```bash
python "WEEK 1/day2_weather.py"
```

The script prints weather information for both cities. If the API key is invalid or not yet active, it displays an error message.

## Stack

Python, Requests, python-dotenv, OpenWeather API
