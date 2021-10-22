import os
import time
import uuid

import telebot
import config
from PIL import Image

from face.face import recognize

bot = telebot.TeleBot(config.TOKEN)
statuses = {}  # statuses[user] = user_status
titles = {}  # titles[user] = user_title
emojis = ['😂', '😍', '🤯', '😢', '🤩', '😴', '💡', '☁️', '🤧', '🥳', '🥰', '😤', '😘', '🤬', '😅', '👍', '👎', '✌️',
          '🤭', '👊', '👐', '🤞', '🤫', '🤔', '😜', '😧', '🙄', '😳', '😡', '😃', '😔', '😉', '👋', '🤙', '❤️', '😬',
          '🙋‍♀️', '😌', '😏', '💁‍♀️', '🙏', '🙅‍♀️', '👩‍💻', '🤦‍♀️', '🤷‍♀️']


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id,
                     'Привет!👋\n\n Я стикер-бот для создания собственных memoji.\n\n Если хочешь получить '
                     'свой стикер-пак, отправь команду /createstickerpack .')


@bot.message_handler(commands=['createstickerpack'])
def init_creation(message):
    bot.send_message(message.chat.id, 'Отправь мне свое фото. \n\nЕсть несколько условий:\n'
                                      '✅️ важно, чтобы на фотографии было одно лицо;\n'
                                      '✅️ для более высокой точности сделай фотографию при хорошем освещении.\n\n'
                                      'Пример фотографии:')
    bot.send_photo(message.chat.id, open(r'example.jpg', 'rb'))
    statuses[message.chat.id] = 'init'


@bot.message_handler(content_types=['text'])
def unrecognized_message(message):

    if statuses.get(message.chat.id) == 'preparing stickerpack':
        bot.send_message(message.chat.id, 'Пока не готов к общению, собираю твой стикерпак. Это может занять '
                                          'некоторое время.')
        return

    if statuses.get(message.chat.id) != 'waiting title':
        bot.send_message(message.chat.id, 'Не понимаю тебя 😣 \nДля создания стикерпака отправь команду '
                                          '/createstickerpack')
        return

    titles[message.chat.id] = message.text
    statuses[message.chat.id] = 'preparing stickerpack'


i = 34  # убрать


@bot.message_handler(content_types=['sticker'])
# убрать, после того как соберем все стикосы
def collect_stickers(message):
    global i
    user_photo_id = message.sticker.file_id
    file_info = bot.get_file(user_photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("sticker.webp", 'wb') as user_photo:
        user_photo.write(downloaded_file)
    user_photo.close()
    user_photo = Image.open("sticker.webp")
    user_photo.save(r'dump\\' + str(i) + '.webp')
    user_photo.close()
    bot.send_message(message.chat.id, str(i))
    i += 1


@bot.message_handler(commands=['undo'])
def del_previous(message):
    global i
    i -= 1
    bot.send_message(message.chat.id, 'Последний сохраненный стикер:')
    bot.send_sticker(message.chat.id, open(r'dump/' + str(i) + '.webp', 'rb'))


@bot.message_handler(content_types=['photo'])
def create_stickerpack(message):

    if statuses.get(message.chat.id) is None or statuses[message.chat.id] != 'init':
        bot.send_message(message.chat.id, 'Для создания стикерпака отправь команду /createstickerpack')
        return

    bot.send_message(message.chat.id, 'Круто! Осталось придумать название для стикерпака 👇')
    statuses[message.chat.id] = 'waiting title'

    user_photo_id = message.photo[-1].file_id
    file_info = bot.get_file(user_photo_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("image.png", 'wb') as user_photo:
        user_photo.write(downloaded_file)
    # ERROR - TeleBot: "A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request:
    # file is too big"
    user_photo.close()

    # res = recognize(os.getcwd() + r'\image.png')
    res = 1

    stickerpack_name = 'cat' + uuid.uuid4().hex[0:30] + '_by_sticker_box_bot'

    start_time = time.perf_counter()
    while statuses[message.chat.id] != 'preparing stickerpack':
        if time.perf_counter() - start_time > 120:
            statuses[message.chat.id] = 'timeout'
            return
        time.sleep(1)
    if statuses[message.chat.id] == 'timeout':
        bot.send_message(message.chat.id, 'Прости, но я не могу ждать так долго. Ничего личного, только бизнес.')
        bot.send_message(message.chat.id, 'Если захочешь попробовать еще раз, отправь команду /createstickerpack')
        statuses.pop(message.chat.id)
        return
    title = titles[message.chat.id]
    bot.send_message(message.chat.id, 'Формирую стикерпак для тебя... Это может занять какое-то время...')
    # можно тут скинуть какой-то текст, типа забавного факта или задачки, потому что ждать придется долго
    # о, или можно кидать процент выполнения (типа 10% 25% ...)

    # TODO: лучше этот кусок кода сделать один раз самим для каждой папки, чтобы на него время не уходило каждый раз
    bandit = Image.open('stickers/set' + str(res) + '/9.webp')
    bandit = bandit.resize((503, 512), Image.ANTIALIAS)
    bandit.save('stickers/set' + str(res) + '/9.webp')
    bandit.close()
    thumb = Image.open('stickers/set' + str(res) + '/18.webp')
    thumb = thumb.resize((100, 100), Image.ANTIALIAS)
    thumb.save('stickers/set' + str(res) + '/thumb.webp')
    thumb.close()

    bot.create_new_sticker_set(message.chat.id, stickerpack_name, title, emojis[0],
                               open('stickers/set1/1.webp', 'rb'), None)

    for n in range(2, 46):
        if n == 40:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '💁‍♂️' + '💁',
                                   open('stickers/set' + str(res) + '/' + str(n) + '.webp', 'rb'), None)
            continue
        if n == 42:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '🙅‍♂️' + '🙅',
                                   open('stickers/set' + str(res) + '/' + str(n) + '.webp', 'rb'), None)
            continue
        if n == 43:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '👨‍💻' + '🧑‍💻',
                                   open('stickers/set' + str(res) + '/' + str(n) + '.webp', 'rb'), None)
            continue
        if n == 44:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '🤦‍♂️' + '🤦',
                                   open('stickers/set' + str(res) + '/' + str(n) + '.webp', 'rb'), None)
            continue
        if n == 45:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '🤷‍♂️' + '🤷',
                                   open('stickers/set' + str(res) + '/' + str(n) + '.webp', 'rb'), None)
            continue
        bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n-1],
                               open('stickers/set' + str(res) + '/' + str(n) + '.webp', 'rb'), None)

    # TODO: check what functions return
    thumb = open('stickers/set' + str(res) + '/thumb.webp', 'rb')
    bot.set_sticker_set_thumb(stickerpack_name, message.chat.id, thumb)
    thumb.close()

    link = 'https://telegram.me/addstickers/' + stickerpack_name
    href = "<a href='" + link + "'>" + title + "</a>"
    bot.send_message(message.chat.id, 'Готово! Твой стикерпак: ' + href, parse_mode='HTML')

    statuses.pop(message.chat.id)
    titles.pop(message.chat.id)


# RUN
bot.polling(none_stop=True, timeout=100000)
