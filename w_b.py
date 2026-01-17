import asyncio
import datetime
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = '8156447633:AAFFqEFxNo3oIG9zMRYZsVBoq1n3VImHeNc'
WEATHER_TOKEN = '06eab615f6f5b38b7051e37f3919ae02'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply("🌤 Привет! Я Погода-Бот. Назовите город, получите точный прогноз и не только). Поймаем солнце или спрячемся от дождя? 😉!")

@dp.message()
async def get_weather(message: Message):
    city = message.text.strip()
    print(f"Ищю город: {city}")
    
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'lang': 'ru',
            'units': 'metric',
            'appid': WEATHER_TOKEN
        }
        
        response = requests.get(url, params=params)
        print(f"Статус ответа: {response.status_code}")
        print(f"Ответ API: {response.text}")
        
        data = response.json()
        
        if response.status_code != 200:
            await message.reply("❌ Такого города не существует(( Попробуй ещё раз😉")
            return
        
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = round(data["main"]["pressure"] / 1.333)
        wind = data["wind"]["speed"]
        
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M')
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M')
        
        weather_main = data["weather"][0]["main"]
        emoji = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧", 
            "Snow": "❄️", "Mist": "🌫"
        }.get(weather_main, "🌤")
        
        text = f"""🌍 Город - {data['name']}
{emoji} Температура - {temp}°C
💧 Влажность -  {humidity}%
📈 Давление - {pressure} мм рт.ст.
💨 Скорость ветра - {wind} м/с
🌄 Рассвет - {sunrise}
🌅 Закад - {sunset}"""
        
        await message.reply(text)
        
    except:
        await message.reply("❌ Проверь название города, а то я такого не знаю 😢")

async def main():
    print("🚀 Я работаю!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
