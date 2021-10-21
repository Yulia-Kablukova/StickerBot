import os

import telebot
import config
from PIL import Image

from face.face import recognize

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome_start(message):
    bot.send_message(message.chat.id, 'Отправьте мне своё фото')


i = 34


@bot.message_handler(content_types=['sticker'])
def send_message(message):
    global i
    user_photo_id = message.sticker.file_id
    file_info = bot.get_file(user_photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("sticker.webp", 'wb') as user_photo:
        user_photo.write(downloaded_file)
    user_photo.close()
    user_photo = Image.open("sticker.webp")
    user_photo.save(r'Y:\Programming\Python\StickerBot\set1\\' + str(i) + '.webp')
    user_photo.close()
    bot.send_message(message.chat.id, str(i))
    i += 1


@bot.message_handler(content_types=['photo'])
def send_message(message):
    user_photo_id = message.photo[-1].file_id
    file_info = bot.get_file(user_photo_id)

    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.png", 'wb') as user_photo:
        user_photo.write(downloaded_file)
    # ERROR - TeleBot: "A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request:
    # file is too big"
    user_photo.close()
    # TODO: name is random (like id), title from user
    bot.send_message(message.chat.id, 'Фото получено')
    id = recognize(os.getcwd() + '\image.png')
    bot.send_message(message.chat.id, id)
    # user_sticker_set_name = "awesome3_stickerpack_by_sticker_box_bot"
    # user_photo = open("somepic.png", 'rb')
    # bot.create_new_sticker_set(message.chat.id, user_sticker_set_name, "Awesome title", "😂", user_photo, None)
    # user_photo.close()
    # user_photo = open("thumb.png", 'rb')
    # bot.set_sticker_set_thumb(user_sticker_set_name, message.chat.id, user_photo)
    #user_photo.close()
    #bot.send_message(message.chat.id, "Фото получено")
    #bot.send_message(message.chat.id, "https://telegram.me/addstickers/" + user_sticker_set_name)


# RUN
bot.polling(none_stop=True, timeout=100000)
