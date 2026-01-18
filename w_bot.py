import asyncio
import datetime
import requests
import math
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from enum import Enum
from typing import Dict, List, Tuple

BOT_TOKEN = '8156447633:AAFFqEFxNo3oIG9zMRYZsVBoq1n3VImHeNc'
WEATHER_TOKEN = '06eab615f6f5b38b7051e37f3919ae02'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ========== НЕСТАНДАРТНЫЕ ВОЗМОЖНОСТИ ==========

class ClothingType(Enum):
    """Типы одежды"""
    HEAD = "голова"
    UPPER = "верх"
    LOWER = "низ"
    FOOT = "ноги"
    ACCESSORIES = "аксессуары"

class ActivityType(Enum):
    """Типы активностей"""
    RUNNING = "бег"
    CYCLING = "велосипед"
    HIKING = "поход"
    FISHING = "рыбалка"
    PHOTOGRAPHY = "фотография"

class HealthRisk(Enum):
    """Медицинские риски"""
    JOINTS = "суставы"
    MIGRAINE = "мигрень"
    ALLERGY = "аллергия"
    COLD = "простуда"

# ========== ПОДБОР ОДЕЖДЫ ==========

def get_clothing_recommendations(temp: float, weather_condition: str, wind_speed: float) -> Dict[ClothingType, List[str]]:
    """Рекомендации по одежде"""
    recommendations = {
        ClothingType.HEAD: [],
        ClothingType.UPPER: [],
        ClothingType.LOWER: [],
        ClothingType.FOOT: [],
        ClothingType.ACCESSORIES: []
    }
    
    # Голова
    if temp < 10:
        recommendations[ClothingType.HEAD].append("🧢 Шапка")
    if temp < 0:
        recommendations[ClothingType.HEAD].append("🎩 Теплая шапка")
    if temp > 25 and weather_condition == "Clear":
        recommendations[ClothingType.HEAD].append("👒 Панама/кепка")
    
    # Верх
    if temp < -15:
        recommendations[ClothingType.UPPER].append("🧥 Пуховик + термобелье")
    elif temp < -5:
        recommendations[ClothingType.UPPER].append("🧥 Теплая зимняя куртка")
    elif temp < 5:
        recommendations[ClothingType.UPPER].append("🧥 Демисезонная куртка")
    elif temp < 15:
        recommendations[ClothingType.UPPER].append("🧥 Ветровка или кофта")
    elif temp < 20:
        recommendations[ClothingType.UPPER].append("👕 Футболка + легкая куртка")
    else:
        recommendations[ClothingType.UPPER].append("👕 Футболка/майка")
    
    # Низ
    if temp < -10:
        recommendations[ClothingType.LOWER].append("👖 Термобелье + теплые штаны")
    elif temp < 0:
        recommendations[ClothingType.LOWER].append("👖 Утепленные штаны/джинсы")
    elif temp < 15:
        recommendations[ClothingType.LOWER].append("👖 Джинсы/брюки")
    else:
        recommendations[ClothingType.LOWER].append("🩳 Шорты/легкие штаны")
    
    # Обувь
    if temp < -5 or weather_condition in ["Snow", "Rain"]:
        recommendations[ClothingType.FOOT].append("🥾 Непромокаемая обувь")
    if temp < -10:
        recommendations[ClothingType.FOOT].append("👢 Утепленные ботинки")
    elif temp < 5:
        recommendations[ClothingType.FOOT].append("👞 Закрытая обувь")
    elif temp > 20:
        recommendations[ClothingType.FOOT].append("👟 Сандалии/кроссовки")
    
    # Аксессуары
    if temp < 5:
        recommendations[ClothingType.ACCESSORIES].append("🧤 Перчатки")
        recommendations[ClothingType.ACCESSORIES].append("🧣 Шарф")
    if wind_speed > 10:
        recommendations[ClothingType.ACCESSORIES].append("🌬️ Ветрозащита")
    if weather_condition == "Rain":
        recommendations[ClothingType.ACCESSORIES].append("☔️ Зонт/дождевик")
    if temp > 25:
        recommendations[ClothingType.ACCESSORIES].append("🕶️ Солнцезащитные очки")
        recommendations[ClothingType.ACCESSORIES].append("🧴 Солнцезащитный крем SPF 30+")
    
    return recommendations

def format_clothing_recommendations(recommendations: Dict) -> str:
    """Форматирование рекомендаций по одежде"""
    text = "👕 *Рекомендации по одежде:*\n\n"
    
    for clothing_type, items in recommendations.items():
        if items:
            text += f"*{clothing_type.value.title()}:*\n"
            for item in items:
                text += f"• {item}\n"
            text += "\n"
    
    return text

# ========== СПЕЦИАЛИЗИРОВАННЫЕ РЕКОМЕНДАЦИИ ==========

def get_sports_recommendations(temp: float, weather_condition: str, wind_speed: float, humidity: float) -> str:
    """Рекомендации для спортсменов"""
    recommendations = []
    
    # Бег
    if 10 <= temp <= 25 and weather_condition == "Clear" and wind_speed < 15:
        recommendations.append("🏃 *Идеально для бега:* отличные условия")
    elif temp < 5:
        recommendations.append("🏃 Для бега: наденьте термобелье, разминайтесь дольше")
    elif temp > 30:
        recommendations.append("🏃 Для бега: избегайте дневных часов, пейте больше воды")
    
    # Велоспорт
    if 15 <= temp <= 30 and wind_speed < 10:
        recommendations.append("🚴 *Отлично для велосипеда*")
    elif wind_speed > 20:
        recommendations.append("🚴 Сильный ветер - будьте осторожны на велосипеде")
    
    # Тренировки на улице
    if humidity > 80 and temp > 20:
        recommendations.append("💪 Высокая влажность - снизьте интенсивность тренировок")
    if weather_condition == "Rain":
        recommendations.append("🌧️ Дождь - перенесите тренировку в зал или оденьте непромокаемую одежду")
    
    return "\n".join(recommendations) if recommendations else "✅ Условия для спорта нормальные"

def get_farmer_recommendations(temp: float, weather_condition: str, humidity: float, wind_speed: float) -> str:
    """Рекомендации для фермеров"""
    recommendations = []
    
    # Посев/посадка
    if 10 <= temp <= 25 and weather_condition == "Clear":
        recommendations.append("🌱 *Идеально для посева*")
    elif temp < 5:
        recommendations.append("❌ Температура слишком низкая для посадки")
    
    # Полив
    if humidity < 40 and weather_condition == "Clear":
        recommendations.append("💧 *Требуется полив* - низкая влажность")
    elif humidity > 85:
        recommendations.append("✅ Полив не требуется - высокая влажность")
    
    # Защита растений
    if temp < 0:
        recommendations.append("🌡️ *Защита от заморозков* - укройте растения")
    if wind_speed > 15:
        recommendations.append("💨 *Сильный ветер* - проверьте опоры для растений")
    
    # Уборка урожая
    if weather_condition == "Clear" and humidity < 60:
        recommendations.append("📅 *Хорошо для уборки урожая*")
    
    return "\n".join(recommendations) if recommendations else "✅ Стандартные условия для сельского хозяйства"

def get_traveler_recommendations(temp: float, weather_condition: str, sunrise: str, sunset: str) -> str:
    """Рекомендации для путешественников"""
    recommendations = []
    
    # Фотография
    golden_hour_morning = "06:00-08:00"  # Условно
    golden_hour_evening = "18:00-20:00"  # Условно
    recommendations.append(f"📸 *Золотой час для фото:* {golden_hour_morning} и {golden_hour_evening}")
    
    # Осмотр достопримечательностей
    if weather_condition == "Clear":
        recommendations.append("🏛️ *Отличный день для экскурсий*")
    elif weather_condition == "Rain":
        recommendations.append("🏛️ *Посетите музеи и крытые достопримечательности*")
    
    # Прогулки
    if 15 <= temp <= 25:
        recommendations.append("🚶 *Идеально для пеших прогулок*")
    elif temp > 30:
        recommendations.append("🚶 *Для прогулок выбирайте утренние или вечерние часы*")
    
    # Световой день
    recommendations.append(f"🌅 *Световой день:* с {sunrise} до {sunset}")
    
    return "\n".join(recommendations)

def get_driver_recommendations(temp: float, weather_condition: str, wind_speed: float, humidity: float) -> str:
    """Рекомендации для водителей"""
    recommendations = []
    
    # Дорожные условия
    if weather_condition == "Snow":
        recommendations.append("⚠️ *Гололед!* Используйте зимнюю резину, тормозите плавно")
    elif weather_condition == "Rain":
        recommendations.append("⚠️ *Мокрая дорога!* Увеличьте дистанцию, снизьте скорость на 20%")
    elif temp < 3 and humidity > 80:
        recommendations.append("⚠️ *Риск гололеда!* Будьте осторожны на мостах и в низинах")
    
    # Видимость
    if weather_condition == "Mist":
        recommendations.append("🌫️ *Туман!* Включите противотуманные фары, снизьте скорость")
    
    # Ветер
    if wind_speed > 15:
        recommendations.append("💨 *Сильный ветер!* Держите руль крепче, осторожно с фурами")
    
    # Температура в салоне
    if temp < -10:
        recommendations.append("❄️ *Прогревайте двигатель 5-10 минут*, проверьте антифриз")
    elif temp > 30:
        recommendations.append("🔥 *Кондиционер на 22-24°C*, не направляйте на лицо")
    
    # Давление в шинах
    if temp > 10:  # Нужно хранить предыдущую температуру
        recommendations.append("🔄 При резком похолодании проверьте давление в шинах")
    
    return "\n".join(recommendations) if recommendations else "✅ Дорожные условия нормальные"

# ========== МЕДИЦИНСКИЕ ИНДЕКСЫ ==========

def calculate_health_indices(temp: float, pressure: float, humidity: float, 
                             weather_condition: str, wind_speed: float) -> Dict[str, Tuple[int, str]]:
    """Расчет медицинских индексов"""
    
    indices = {}
    
    # 1. Индекс для суставов (0-10, где 10 - максимальный дискомфорт)
    joints_risk = 0
    
    # Влажность и холод - главные враги суставов
    if humidity > 85:
        joints_risk += 3
    if temp < 10:
        joints_risk += 4
    if pressure < 730:  # Низкое давление
        joints_risk += 2
    if weather_condition in ["Rain", "Snow"]:
        joints_risk += 2
    
    joints_risk = min(joints_risk, 10)
    joints_desc = {
        0: "✅ Низкий риск",
        1: "✅ Минимальный риск",
        2: "✅ Незначительный риск",
        3: "⚠️ Умеренный риск",
        4: "⚠️ Повышенный риск",
        5: "⚠️ Средний риск",
        6: "🔴 Высокий риск",
        7: "🔴 Очень высокий риск",
        8: "🔴 Критический риск",
        9: "🔴 Экстремальный риск",
        10: "🔴 Максимальный риск"
    }.get(joints_risk, "✅ Низкий риск")
    
    indices["joints"] = (joints_risk, joints_desc)
    
    # 2. Индекс мигрени (0-10)
    migraine_risk = 0
    
    # Резкие перепады давления и температуры
    pressure_change = 0  # Нужно хранить предыдущее давление
    if abs(pressure_change) > 5:  # Резкое изменение давления
        migraine_risk += 4
    if temp > 10:  # Резкое изменение температуры
        migraine_risk += 3
    if humidity > 80:
        migraine_risk += 2
    if wind_speed > 15:
        migraine_risk += 1
    
    migraine_risk = min(migraine_risk, 10)
    migraine_desc = {
        0: "✅ Благоприятно",
        1: "✅ Низкий риск",
        2: "✅ Незначительный риск",
        3: "⚠️ Умеренный риск",
        4: "⚠️ Повышенный риск",
        5: "⚠️ Средний риск",
        6: "🔴 Высокий риск",
        7: "🔴 Очень высокий риск",
        8: "🔴 Критический риск",
        9: "🔴 Экстремальный риск",
        10: "🔴 Максимальный риск"
    }.get(migraine_risk, "✅ Низкий риск")
    
    indices["migraine"] = (migraine_risk, migraine_desc)
    
    # 3. Индекс аллергии (0-10)
    allergy_risk = 0
    
    # Весенний период (апрель-май) - цветение
    month = datetime.datetime.now().month
    if 4 <= month <= 6:
        allergy_risk += 4
    # Ветер разносит пыльцу
    if 5 <= wind_speed <= 15:
        allergy_risk += 3
    # Сухая погода способствует распространению пыльцы
    if humidity < 40:
        allergy_risk += 2
    # Ясная погода - высокая концентрация пыльцы
    if weather_condition == "Clear":
        allergy_risk += 1
    
    allergy_risk = min(allergy_risk, 10)
    allergy_desc = {
        0: "✅ Низкий риск",
        1: "✅ Минимальный риск",
        2: "✅ Незначительный риск",
        3: "⚠️ Умеренный риск",
        4: "⚠️ Повышенный риск",
        5: "⚠️ Средний риск",
        6: "🔴 Высокий риск",
        7: "🔴 Очень высокий риск",
        8: "🔴 Критический риск",
        9: "🔴 Экстремальный риск",
        10: "🔴 Максимальный риск"
    }.get(allergy_risk, "✅ Низкий риск")
    
    indices["allergy"] = (allergy_risk, allergy_desc)
    
    # 4. Индекс простуды (0-10)
    cold_risk = 0
    
    # Низкая температура и высокая влажность
    if temp < 5:
        cold_risk += 4
    if 5 <= temp < 15:
        cold_risk += 2
    if humidity > 80:
        cold_risk += 3
    if wind_speed > 10:
        cold_risk += 2  # Ветер охлаждает тело
    if weather_condition in ["Rain", "Snow"]:
        cold_risk += 1
    
    cold_risk = min(cold_risk, 10)
    cold_desc = {
        0: "✅ Низкий риск",
        1: "✅ Минимальный риск",
        2: "✅ Незначительный риск",
        3: "⚠️ Умеренный риск",
        4: "⚠️ Повышенный риск",
        5: "⚠️ Средний риск",
        6: "🔴 Высокий риск",
        7: "🔴 Очень высокий риск",
        8: "🔴 Критический риск",
        9: "🔴 Экстремальный риск",
        10: "🔴 Максимальный риск"
    }.get(cold_risk, "✅ Низкий риск")
    
    indices["cold"] = (cold_risk, cold_desc)
    
    return indices

def format_health_indices(indices: Dict) -> str:
    """Форматирование медицинских индексов"""
    text = "🏥 *Медицинские индексы:*\n\n"
    
    emoji_map = {
        "joints": "🦵",
        "migraine": "🤕", 
        "allergy": "🤧",
        "cold": "🤒"
    }
    
    name_map = {
        "joints": "Суставы",
        "migraine": "Мигрень",
        "allergy": "Аллергия",
        "cold": "Простуда"
    }
    
    for key, (risk, desc) in indices.items():
        # Создаем график риска [■■■■□□□□□□]
        bars = 10
        filled = int(risk)
        empty = bars - filled
        graph = "🔴" * filled + "⚪️" * empty
        
        text += f"{emoji_map[key]} *{name_map[key]}:* {risk}/10\n"
        text += f"{graph}\n"
        text += f"{desc}\n\n"
    
    return text

# ========== ОСНОВНЫЕ КОМАНДЫ БОТА ==========

@dp.message(Command("start"))
async def start_command(message: Message):
    """Начальная команда"""
    await message.reply(
        "🌤 Привет! Я Погода-Бот. Назовите город, получите точный прогноз и не только). "
        "Поймаем солнце или спрячемся от дождя? 😉!\n\n"
        "*Доступные команды:*\n"
        "• Напишите название города - обычный прогноз\n"
        "• /clothing [город] - рекомендации по одежде\n"
        "• /sports [город] - для спортсменов\n"
        "• /farmer [город] - для фермеров\n"
        "• /traveler [город] - для путешественников\n"
        "• /driver [город] - для водителей\n"
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
    
    await process_weather_with_function(message, city, "clothing")

@dp.message(Command("sports"))
async def sports_command(message: Message):
    """Рекомендации для спортсменов"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /sports [город]")
        return
    
    await process_weather_with_function(message, city, "sports")

@dp.message(Command("farmer"))
async def farmer_command(message: Message):
    """Рекомендации для фермеров"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /farmer [город]")
        return
    
    await process_weather_with_function(message, city, "farmer")

@dp.message(Command("traveler"))
async def traveler_command(message: Message):
    """Рекомендации для путешественников"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /traveler [город]")
        return
    
    await process_weather_with_function(message, city, "traveler")

@dp.message(Command("driver"))
async def driver_command(message: Message):
    """Рекомендации для водителей"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /driver [город]")
        return
    
    await process_weather_with_function(message, city, "driver")

@dp.message(Command("health"))
async def health_command(message: Message):
    """Медицинские индексы"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /health [город]")
        return
    
    await process_weather_with_function(message, city, "health")

@dp.message(Command("full"))
async def full_analysis_command(message: Message):
    """Полный анализ погоды"""
    try:
        city = message.text.split(maxsplit=1)[1].strip()
    except IndexError:
        await message.reply("❌ Укажите город: /full [город]")
        return
    
    await process_weather_with_function(message, city, "full")

# ========== ОБРАБОТЧИК ПОГОДЫ ==========

async def process_weather_with_function(message: Message, city: str, function: str):
    """Обработка погоды с вызовом специфической функции"""
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
            await message.reply("❌ Такого города не существует(( Попробуй ещё раз😉")
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
        
        # Вызываем нужную функцию
        if function == "clothing":
            clothing_recs = get_clothing_recommendations(temp, weather_main, wind)
            clothing_text = format_clothing_recommendations(clothing_recs)
            await message.reply(base_text + "\n" + clothing_text, parse_mode="Markdown")
            
        elif function == "sports":
            sports_text = get_sports_recommendations(temp, weather_main, wind, humidity)
            await message.reply(base_text + "\n" + sports_text, parse_mode="Markdown")
            
        elif function == "farmer":
            farmer_text = get_farmer_recommendations(temp, weather_main, humidity, wind)
            await message.reply(base_text + "\n" + farmer_text, parse_mode="Markdown")

        elif function == "traveler":
            traveler_text = get_traveler_recommendations(temp, weather_main, sunrise, sunset)
            await message.reply(base_text + "\n" + traveler_text, parse_mode="Markdown")
            
        elif function == "driver":
            driver_text = get_driver_recommendations(temp, weather_main, wind, humidity)
            await message.reply(base_text + "\n" + driver_text, parse_mode="Markdown")
            
        elif function == "health":
            health_indices = calculate_health_indices(temp, pressure, humidity, weather_main, wind)
            health_text = format_health_indices(health_indices)
            await message.reply(base_text + "\n" + health_text, parse_mode="Markdown")
            
        elif function == "full":
            # Полный анализ
            clothing_recs = get_clothing_recommendations(temp, weather_main, wind)
            clothing_text = format_clothing_recommendations(clothing_recs)
            
            sports_text = get_sports_recommendations(temp, weather_main, wind, humidity)
            farmer_text = get_farmer_recommendations(temp, weather_main, humidity, wind)
            traveler_text = get_traveler_recommendations(temp, weather_main, sunrise, sunset)
            driver_text = get_driver_recommendations(temp, weather_main, wind, humidity)
            
            health_indices = calculate_health_indices(temp, pressure, humidity, weather_main, wind)
            health_text = format_health_indices(health_indices)
            
            full_text = (
                base_text + "\n" +
                "="*30 + "\n" +
                clothing_text + "\n" +
                "🏃 *Для спортсменов:*\n" + sports_text + "\n\n" +
                "👨‍🌾 *Для фермеров:*\n" + farmer_text + "\n\n" +
                "🧳 *Для путешественников:*\n" + traveler_text + "\n\n" +
                "🚗 *Для водителей:*\n" + driver_text + "\n\n" +
                health_text
            )
            
            # Разбиваем длинное сообщение на части
            if len(full_text) > 4000:
                parts = [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]
                for part in parts:
                    await message.reply(part, parse_mode="Markdown")
            else:
                await message.reply(full_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.reply("❌ Произошла ошибка при обработке запроса")

# ========== СТАНДАРТНЫЙ ОТВЕТ НА ГОРОД ==========

@dp.message()
async def get_weather(message: Message):
    """Стандартный ответ на название города"""
    city = message.text.strip()
    
    if city.startswith('/'):
        return  # Игнорируем команды
    
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
            await message.reply("❌ Такого города не существует(( Попробуй ещё раз😉")
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
/sports - для спорта
/farmer - для фермеров
/traveler - для путешествий
/driver - для водителей
/health - медицинские индексы
/full - полный анализ
"""
        
        await message.reply(text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        await message.reply("❌ Проверь название города, а то я такого не знаю 😢")

# ========== ЗАПУСК БОТА ==========

async def main():
    print("🚀 Я работаю с расширенными функциями!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
