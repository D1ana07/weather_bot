import asyncio
import datetime
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

BOT_TOKEN = '8156447633:AAFFqEFxNo3oIG9zMRYZsVBoq1n3VImHeNc'
WEATHER_TOKEN = '06eab615f6f5b38b7051e37f3919ae02'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== РЕКОМЕНДАЦИИ ПО ОДЕЖДЕ ==========

def get_clothing_recommendations(temp: float, weather_condition: str, wind_speed: float) -> str:
    """Рекомендации по одежде"""
    recommendations = []
    
    # Верх
    if temp < -15:
        recommendations.append("🧥 Пуховик + термобелье")
    elif temp < -5:
        recommendations.append("🧥 Теплая зимняя куртка")
    elif temp < 5:
        recommendations.append("🧥 Демисезонная куртка")
    elif temp < 15:
        recommendations.append("🧥 Ветровка или кофта")
    elif temp < 20:
        recommendations.append("👕 Футболка + легкая куртка")
    else:
        recommendations.append("👕 Футболка/майка")
    
    # Низ
    if temp < -10:
        recommendations.append("👖 Термобелье + теплые штаны")
    elif temp < 0:
        recommendations.append("👖 Утепленные штаны/джинсы")
    elif temp < 15:
        recommendations.append("👖 Джинсы/брюки")
    else:
        recommendations.append("🩳 Шорты/легкие штаны")
    
    # Голова и аксессуары
    if temp < 10:
        recommendations.append("🧢 Шапка")
    if temp < 0:
        recommendations.append("🎩 Теплая шапка")
    if temp > 25 and weather_condition == "Clear":
        recommendations.append("👒 Панама/кепка")
    if temp < 5:
        recommendations.append("🧤 Перчатки, 🧣 Шарф")
    if wind_speed > 10:
        recommendations.append("🌬️ Ветрозащита")
    if weather_condition == "Rain":
        recommendations.append("☔️ Зонт/дождевик")
    if temp > 25:
        recommendations.append("🕶️ Солнцезащитные очки, 🧴 Солнцезащитный крем")
    
    # Обувь
    if temp < -5 or weather_condition in ["Snow", "Rain"]:
        recommendations.append("🥾 Непромокаемая обувь")
    elif temp < 5:
        recommendations.append("👞 Закрытая обувь")
    elif temp > 20:
        recommendations.append("👟 Сандалии/кроссовки")
    
    return "\n".join(f"• {item}" for item in recommendations)

# ========== МЕДИЦИНСКИЕ ИНДЕКСЫ ==========

def calculate_health_indices(temp: float, pressure: float, humidity: float, weather_condition: str) -> str:
    """Расчет медицинских индексов"""
    indices = []
    
    # Индекс для суставов
    joints_risk = 0
    if humidity > 85:
        joints_risk += 3
    if temp < 10:
        joints_risk += 4
    if pressure < 730:
        joints_risk += 2
    if weather_condition in ["Rain", "Snow"]:
        joints_risk += 2
    joints_risk = min(joints_risk, 10)
    
    # Индекс мигрени
    migraine_risk = 0
    if humidity > 80:
        migraine_risk += 2
    migraine_risk = min(migraine_risk, 10)
    
    # Индекс аллергии
    allergy_risk = 0
    month = datetime.datetime.now().month
    if 4 <= month <= 6:
        allergy_risk += 3
    if humidity < 40:
        allergy_risk += 2
    if weather_condition == "Clear":
        allergy_risk += 1
    allergy_risk = min(allergy_risk, 10)
    
    # Индекс простуды
    cold_risk = 0
    if temp < 5:
        cold_risk += 4
    elif 5 <= temp < 15:
        cold_risk += 2
    if humidity > 80:
        cold_risk += 3
    if weather_condition in ["Rain", "Snow"]:
        cold_risk += 1
    cold_risk = min(cold_risk, 10)
    
    # Форматирование
    health_data = [
        ("🦵 Суставы", joints_risk),
        ("🤕 Мигрень", migraine_risk),
        ("🤧 Аллергия", allergy_risk),
        ("🤒 Простуда", cold_risk)
    ]
    
    for name, risk in health_data:
        bars = "🔴" * risk + "⚪️" * (10 - risk)
        indices.append(f"{name}: {risk}/10\n{bars}")
    
    return "\n\n".join(indices)

# ========== ОСНОВНЫЕ КОМАНДЫ БОТА ==========

@dp.message(Command("start"))
async def start_command(message: Message):
    """Начальная команда"""
    await message.reply(
        "🌤 Привет! Я Погода-Бот. Назовите город, получите точный прогноз.\n\n"
        "*Доступные команды:*\n"
        "• Напишите название города - обычный прогноз\n"
        "• /clothing [город] - рекомендации по одежде\n"
        "• /health [город] - медицинские индексы\n"
        "• /full [город] - полный анализ погоды",
        parse_mode="Markdown"
    )

@dp.message(Command("clothing"))
async def clothing_command(message: Message):
    """Рекомендации по одежде"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /clothing [город]")
        return
    
    await process_weather(message, city, "clothing")

@dp.message(Command("health"))
async def health_command(message: Message):
    """Медицинские индексы"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /health [город]")
        return
    
    await process_weather(message, city, "health")

@dp.message(Command("full"))
async def full_analysis_command(message: Message):
    """Полный анализ погоды"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /full [город]")
        return
    
    await process_weather(message, city, "full")

# ========== ОБРАБОТЧИК ПОГОДЫ ==========

async def process_weather(message: Message, city: str, mode: str):
    """Обработка погоды"""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'lang': 'ru',
            'units': 'metric',
            'appid': WEATHER_TOKEN
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code != 200:
            await message.reply("❌ Город не найден")
            return
        
        # Извлекаем данные
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = round(data["main"]["pressure"] / 1.333)
        wind = data["wind"]["speed"]
        
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M')
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M')
        
        weather_main = data["weather"][0]["main"]
        weather_description = data["weather"][0]["description"]
        
        emoji = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧", 
            "Snow": "❄️", "Mist": "🌫", "Drizzle": "🌦",
            "Thunderstorm": "⛈", "Fog": "🌫"
        }.get(weather_main, "🌤")
        
        # Базовый текст
        base_text = f"""🌍 *{data['name']}*
{emoji} *{temp}°C* ({weather_description})
💧 Влажность: {humidity}%
📈 Давление: {pressure} мм рт.ст.
💨 Ветер: {wind} м/с
🌄 Рассвет: {sunrise}
🌅 Закат: {sunset}
"""
        
        if mode == "clothing":
            clothing = get_clothing_recommendations(temp, weather_main, wind)
            await message.reply(f"{base_text}\n👕 *Что надеть:*\n{clothing}", parse_mode="Markdown")
            
        elif mode == "health":
            health = calculate_health_indices(temp, pressure, humidity, weather_main)
            await message.reply(f"{base_text}\n🏥 *Медицинские индексы:*\n{health}", parse_mode="Markdown")
            
        elif mode == "full":
            clothing = get_clothing_recommendations(temp, weather_main, wind)
            health = calculate_health_indices(temp, pressure, humidity, weather_main)
            
            full_text = f"""{base_text}
{'='*30}

👕 *Что надеть:*
{clothing}

{'='*30}

🏥 *Медицинские индексы:*
{health}
"""
            await message.reply(full_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.reply("❌ Ошибка при обработке запроса")

# ========== СТАНДАРТНЫЙ ОТВЕТ НА ГОРОД ==========

@dp.message()
async def get_weather(message: Message):
    """Стандартный ответ на название города"""
    city = message.text.strip()
    
    if city.startswith('/'):
        return
    
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'lang': 'ru',
            'units': 'metric',
            'appid': WEATHER_TOKEN
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code != 200:
            await message.reply("❌ Город не найден")
            return
        
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        pressure = round(data["main"]["pressure"] / 1.333)
        wind = data["wind"]["speed"]
        
        sunrise = datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M')
        sunset = datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M')
        
        weather_main = data["weather"][0]["main"]
        weather_description = data["weather"][0]["description"]
        
        emoji = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧", 
            "Snow": "❄️", "Mist": "🌫", "Drizzle": "🌦",
            "Thunderstorm": "⛈", "Fog": "🌫"
        }.get(weather_main, "🌤")
        
        # Базовая рекомендация по одежде
        if temp < 0:
            clothing = "❄️ Оденьтесь очень тепло!"
        elif temp < 10:
            clothing = "🧥 Наденьте куртку"
        elif temp < 20:
            clothing = "🧥 Легкая куртка или кофта"
        else:
            clothing = "👕 Легкая одежда"
        
        text = f"""🌍 *{data['name']}*
{emoji} *{temp}°C* ({weather_description})
💧 Влажность: {humidity}%
📈 Давление: {pressure} мм рт.ст.
💨 Ветер: {wind} м/с
🌄 Рассвет: {sunrise}
🌅 Закат: {sunset}

{clothing}

*Для подробного анализа используйте:*
/clothing - что надеть
/health - медицинские индексы
/full - полный анализ
"""
        
        await message.reply(text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.reply("❌ Ошибка при обработке запроса")

# ========== ЗАПУСК БОТА ==========

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
