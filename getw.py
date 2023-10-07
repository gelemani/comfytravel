import telebot, requests as r
from config import tele_token, API


bot = telebot.TeleBot(tele_token)


def main():
    @bot.message_handler(commands=['help', 'start'])
    def start(message):
        bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAEHBdljqvsBs-oMIilMOfg-FJYK7TBcFgACfhoAAnMsOUgm5dy7Utq1lCwE")
        msg = bot.send_message(message.chat.id,'Приветствую тебя, {0.first_name}!'.format(message.from_user))
        bot.register_next_step_handler(msg, flight)


origin = None
destination = None
departure_date = None
return_date = None
origin_name = None
destination_name = None
is_true = True


@bot.message_handler(commands=['flights'])
def flight(message):
    bot.send_message(message.chat.id, "Откуда и куда полетим? ✈️")
    
    @bot.message_handler(content_types=['text'])
    def handle_text_1(message):
        global origin, destination, departure_date, return_date, origin_name, destination_name, is_true
        mesg = message.text
        try:
            url = f'https://www.travelpayouts.com/widgets_suggest_params?q={mesg}'
            request = r.get(url)
            data = request.json()
            origin = data['origin']['iata']
            origin_name = data['origin']['name']
            destination = data['destination']['iata']
            destination_name = data['destination']['name']
            is_true = True
            print(data, origin, destination)

        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "Что-то пошло не так...😒")
            is_true = False

        if is_true:
            bot.register_next_step_handler(bot.send_message(message.chat.id, 'Введите дату вылета (в формате год-месяц-день)'), date_1)
        else:
            bot.register_next_step_handler(bot.send_message(message.chat.id, 'Откуда и куда полетим? ✈️'), handle_text_1)


    @bot.message_handler(content_types=['text'])
    def date_1(message):
        global departure_date
        departure_date = message.text
        msg = bot.send_message(message.chat.id, 'Введите дату возвращения (в формате год-месяц-день)')
        bot.register_next_step_handler(msg, date_2)


    @bot.message_handler(content_types=['text'])
    def date_2(message):
        global origin, destination, departure_date, return_date, origin_name, destination_name, is_true
        # bot.send_message(message.chat.id, '')
        return_date = message.text
        bot.send_message(message.chat.id, f"""\
Поиск
Место отправления: {origin_name} 🛫
Место прибытия: {destination_name} 🛬
Дата отправления: {departure_date} 🕛
Дата возвращения: {return_date} 🕝
        """)
    
        try:    
            URL = f'https://api.travelpayouts.com/aviasales/v3/prices_for_dates?origin={origin}&destination={destination}&currency=rub&departure_at={departure_date}&return_at={return_date}&sorting=price&direct=true&limit=10&token={API}'
            request = r.get(URL)
            data = request.json()
            link = data['data'][0]['link']
            l = 'https://www.aviasales.ru' + link
            bot.send_message(message.chat.id, l)
            bot.send_message(message.chat.id, 'Приятного полета 🌍✈️')
        
        
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, "Что-то пошло не так...😒")
            is_true = False
            bot.register_next_step_handler(bot.send_message(message.chat.id, 'Откуда и куда полетим? ✈️'), handle_text_1)



if __name__ == "__main__":
    main()

bot.polling(none_stop=True)
