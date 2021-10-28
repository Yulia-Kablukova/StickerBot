import os
import time
import uuid
import telebot
import config
from telebot import types
from face.face import recognize

bot = telebot.TeleBot(config.TOKEN)
logs_chat_id = '-1001766112276'
statuses = {}
genders = {}
titles = {}
emojis = ['🤙', '❤️', '👋', '😂', '😍', '🤯', '😴', '🤩', '😢', '💡', '☁️', '🤧', '😤', '🥰', '🥳', '😘', '🤬', '😅',
          '😏', '😌', '😬', '👍', '👎', '✌️', '👐', '👊', '🤭', '💁‍♀️', '🙏', '🙅‍♀️', '🤞', '🤫', '🤔', '😧', '😜',
          '👩‍💻', '🙋‍♀️', '🤷‍♀️', '🤦‍♀️', '🙄', '😳', '😡', '😉', '😔', '😃']


@bot.message_handler(commands=["createstickerpack"])
def init_creation(message):
    statuses[message.chat.id] = 'waiting for button'
    keyboard = types.InlineKeyboardMarkup()
    button_male = types.InlineKeyboardButton(text="мужской", callback_data="male")
    button_female = types.InlineKeyboardButton(text="женский", callback_data="female")
    keyboard.add(button_male, button_female)
    bot.send_message(message.chat.id, "Выбери пол:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def set_gender(call: types.CallbackQuery):
    if statuses.get(call.message.chat.id) != 'waiting for button':
        return

    genders[call.message.chat.id] = call.data
    bot.send_message(call.message.chat.id, 'Отправь мне свое фото. \n\nЕсть несколько условий:\n'
                                      '✅️ важно, чтобы на фотографии было одно лицо;\n'
                                      '✅️ для более высокой точности сделай фотографию при хорошем освещении.\n\n'
                                      'Пример фотографии:')
    bot.send_photo(call.message.chat.id, open(r'example.jpg', 'rb'))
    statuses[call.message.chat.id] = 'init'


@bot.message_handler(content_types=['text'])
def text_message_answer(message):

    if statuses.get(message.chat.id) == 'preparing stickerpack':
        bot.send_message(message.chat.id, 'Пока не готов к общению, собираю твой стикерпак. Это может занять '
                                          'некоторое время.')
        return

    if statuses.get(message.chat.id) != 'waiting title':
        bot.send_message(message.chat.id, 'Не понимаю тебя 😣 \nДля создания стикерпака отправь команду '
                                          '/createstickerpack')
        bot.send_message(logs_chat_id, message.from_user.first_name + ' прислал нераспознанный текст:' + message.text)
        return

    titles[message.chat.id] = message.text
    statuses[message.chat.id] = 'preparing stickerpack'


@bot.message_handler(content_types=['photo'])
def create_stickerpack(message):

    bot.send_message(logs_chat_id, message.from_user.first_name + ' прислал фото:')
    bot.send_photo(logs_chat_id, message.photo[-1].file_id)

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
    user_photo.close()

    res = recognize(os.getcwd() + r'\image.png', genders[message.chat.id])

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
    if res is None:
        bot.send_message(message.chat.id, 'Лицо не распознано, попробуй еще раз с другим фото.')
        statuses.pop(message.chat.id)
        return
    title = titles[message.chat.id]
    bot.send_message(message.chat.id, 'Формирую стикерпак для тебя...\nЭто может занять какое-то время.')
    progress = bot.send_message(message.chat.id, '0%')

    stickers_path = 'stickers/' + genders[message.chat.id] + '/set' + str(res) + '/';
    bot.create_new_sticker_set(message.chat.id, stickerpack_name, title, emojis[0], open(stickers_path + '1.webp', 'rb'), None)

    for n in range(2, 46):
        if n % 6 == 0:
            progress = bot.edit_message_text(str(int(n*100/45)) + '%', progress.chat.id, progress.id)
        if n == 45:
            progress = bot.edit_message_text('100%', progress.chat.id, progress.id)
        if n == 28:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '💁‍♂️' + '💁',
                                   open(stickers_path + str(n) + '.webp', 'rb'), None)
            continue
        if n == 29:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '🙅‍♂️' + '🙅',
                                   open(stickers_path + str(n) + '.webp', 'rb'), None)
            continue
        if n == 35:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '👨‍💻' + '🧑‍💻',
                                   open(stickers_path + str(n) + '.webp', 'rb'), None)
            continue
        if n == 38:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '🤷‍♂️' + '🤷',
                                   open(stickers_path + str(n) + '.webp', 'rb'), None)
            continue
        if n == 39:
            bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1] + '🤦‍♂️' + '🤦',
                                   open(stickers_path + str(n) + '.webp', 'rb'), None)
            continue
        bot.add_sticker_to_set(message.chat.id, stickerpack_name, emojis[n - 1],
                               open(stickers_path + str(n) + '.webp', 'rb'), None)

    thumb = open(stickers_path + 'thumb.webp', 'rb')
    bot.set_sticker_set_thumb(stickerpack_name, message.chat.id, thumb)
    thumb.close()

    link = 'https://telegram.me/addstickers/' + stickerpack_name
    href = "<a href='" + link + "'>" + title + "</a>"
    bot.send_message(message.chat.id, 'Готово! Твой стикерпак: ' + href, parse_mode='HTML')

    statuses.pop(message.chat.id)
    titles.pop(message.chat.id)
    genders.pop(message.chat.id)


# RUN
bot.polling(none_stop=True, timeout=100000)
