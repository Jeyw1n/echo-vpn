from datetime import timedelta

# AI сгенерированная функция. Я не знаю как она работает сполна
def format_remaining_time(remaining_time: timedelta) -> str:
    # Получаем дни, часы и минуты из объекта timedelta
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Формируем строку в нужном формате
    return f"{days}д {hours}ч {minutes}мин"