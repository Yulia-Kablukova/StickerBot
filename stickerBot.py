import telebot
import config

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.send_message(message.chat.id, 'Отправьте мне своё фото')

@bot.message_handler(content_types=['photo'])
def sendMessage(message):
        userPhoto = message.photo[2].file_id
        bot.send_photo(message.chat.id, userPhoto)
        bot.send_message(message.chat.id, 'Фото получено')


#RUN
bot.polling(none_stop=True)
