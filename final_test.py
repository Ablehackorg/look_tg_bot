from random import randint

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from decimal import Decimal
from yandex_geocoder import Client
from language_chose import language_dict as lang

# token = '7632195479:AAEkYb8c04O4e-rUTjVkjNZkQSrnjZzlWMk' ustoz
token= '7766073489:AAHNkeK7zYbKB7c8O2jKjtPYqZ3OX5rSVgI'
channel = ''
user_data = {}
bot = Bot(token=token)
dp = Dispatcher()
lang1=lang()
email = ""
password = ""


# def get_eskiz_token(email, password):
#     url = "https://notify.eskiz.uz/api/auth/login"
#     payload = {
#         'email': email,
#         'password': password
#     }
#     headers = {}
#     response = requests.post(url, data=payload, headers=headers)
#     if response.status_code == 200:  #OK
#         return response.json().get('data', {}).get('token', {})

# def send_sms(phone, token):
#     url = "https://notify.eskiz.uz/api/message/sms/send"
#     payload = {'mobile_phone': phone,
#                'message': 'Bu Eskiz dan test',
#                'from': '4546',
#                'callback_url': 'http://0000.uz/test.php'}
#     headers = {
#         'Authorization': f'Bearer {token}'
#     }
#     response = requests.post(url, headers=headers, data=payload)
#     if response.status_code != 200:
#         raise Exception("SMS yuborishda hatolik")



# @dp.message()
# async def handle_text(message: types.Message):
#     user_id = message.from_user.id
#     lang_user=user_data[user_id]['lang']
#     if message.text == lang1[lang_user]['back']:
#         await back(message)
#     elif user_id not in user_data or message.text == '/start':
#         user_data[user_id] = {}
#         await chose_lang(message)
#     elif 'lang' not in user_data[user_id]:
#         await greeting(message)
#     elif 'code' not in user_data[user_id]:
#         await send_code(message)
#     elif 'verified' != user_data[user_id]['status']:
#         await check_code(message)
#     elif 'check_main_menu' in user_data[user_id]['state']:
#         await check_main_menu(message)
#     elif 'order' in user_data[user_id]['state']:
#         await check_order(message)
#     elif 'get_location' in user_data[user_id]['state']:
#         await check_address(message)
#     elif 'category_menu' in user_data[user_id]['state']:
#         await check_category(message)
#     elif 'item_menu' in user_data[user_id]['state']:
#         await check_item(message)
#     elif 'location' in user_data[user_id]:
#         await address(message)
#     elif 'filial' in user_data[user_id]['state']:
#         await  check_get(message)
@dp.message()
async def handle_text(message: types.Message):
    user_id = message.from_user.id

    # Foydalanuvchi bazada yo‘q bo‘lsa, uni qo‘shish va til tanlatish
    if user_id not in user_data:
        user_data[user_id] = {}
        await chose_lang(message)
        return

    # Agar til hali tanlanmagan bo‘lsa
    if 'lang' not in user_data[user_id]:
        await greeting(message)
        return

    lang_user = user_data[user_id]['lang']

    if message.text == lang1[lang_user]['back']:
        await back(message)
    elif message.text == '/start':
        await chose_lang(message)
    elif 'code' not in user_data[user_id]:
        await send_code(message)
    elif user_data[user_id].get('status') != 'verified':
        await check_code(message)
    elif 'check_main_menu' in user_data[user_id].get('state', ''):
        await check_main_menu(message)
    elif 'order' in user_data[user_id].get('state', ''):
        await check_order(message)
    elif 'get_location' in user_data[user_id].get('state', ''):
        await check_address(message)
    elif 'category_menu' in user_data[user_id].get('state', ''):
        await check_category(message)
    elif 'item_menu' in user_data[user_id].get('state', ''):
        await check_item(message)
    elif 'location' in user_data[user_id]:
        await address(message)
    elif 'filial' in user_data[user_id].get('state', ''):
        await check_get(message)

async def back(message: types.Message):
    user_id = message.from_user.id
    print('back funksiyasi')
    if user_data[user_id]['state'] == 'check_main_menu':
        await main_menu(message)
    elif user_data[user_id]['state'] == 'order':
        await main_menu(message)
    elif user_data[user_id]['state'] == 'location':
        await order(message)
    elif user_data[user_id]['state'] == 'get_location':
        if 'location' in user_data[user_id]:
            del user_data[user_id]['location']
        await ask_location(message)
    elif user_data[user_id]['state'] == 'category_menu':
        if 'filial' in user_data:
            await order(message)
        else:
            await ask_location(message)
    elif user_data[user_id]['state'] == 'item_menu':
        await category_menu(message)
    elif user_data[user_id]['state']=='filial':
        await order(message)
    print('back', user_data)


# async def chose_lang(message: types.Message):
#     user_id= message.from_user.id
#     user_data[user_id]={}
#     buttons= [types.KeyboardButton(text="O'zbekcha"),types.KeyboardButton(text='Русский')]
#     keyboard=types.ReplyKeyboardMarkup(keyboard=buttons,resize_keyboard=True)
#     await message.answer("Assalomu alykum til tanlang. \n"
#     "Здраствуйте выберите язык.",reply_markup=keyboard)
# lang1=lang()
async def chose_lang(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    buttons = [
        [types.KeyboardButton(text="O'zbekcha")],
        [types.KeyboardButton(text='Русский')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer("Assalomu alykum til tanlang.\nЗдраствуйте выберите язык.", reply_markup=keyboard)


async def greeting(message: types.Message):
    user_id = message.from_user.id
    lang_user=message.text

    if lang_user in lang1:
        user_data[user_id]['lang']= lang_user
        username = message.from_user.username
        if username is None:
            username = message.from_user.full_name

        button = [
            [types.KeyboardButton(text=lang1[lang_user]['greeting']['buttons'], request_contact=True)]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
        print(1, user_data)
        await message.answer(f"{lang1[lang_user]['greeting']['hello']}", reply_markup=keyboard)


async def send_code(message: types.Message):
    user_id = message.from_user.id
    lang_user=user_data[user_id]['lang']
    if message.contact is not None:
        phone = message.contact.phone_number
        user_data[user_id]['phone'] = phone
        code = randint(100000, 999999)
        user_data[user_id]['code'] = code
        user_data[user_id]['status'] = 'not verified'
        print(2, user_data)
        # token = get_eskiz_token(email, password)
        try:
            # send_sms(phone, token)
            await message.answer(f"{lang1[lang_user]['send_code']['answer']} `{code}`", parse_mode='MarkdownV2')
        except Exception as ec:
            await message.answer(ec)
    else:
        phone = message.text






async def check_code(message: types.Message):
    user_id = message.from_user.id
    code = user_data[user_id]['code']
    lang_user=user_data[user_id]['lang']
    user_code = message.text
    print(3, user_data)
    if user_code == str(code):
        user_data[user_id]['status'] = 'verified'
        await message.answer(f"{lang1[lang_user]['check_code']['answer'][1]}")
        await main_menu(message)

    else:
        await message.answer(f"{lang1[lang_user]['check_code']['answer'][2]}")


async def main_menu(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['state'] = 'check_main_menu'
    lang_user=user_data[user_id]['lang']
    buttons = [
        [types.KeyboardButton(text=lang1[lang_user]['main_menu']['buttons']['order'])],
        [types.KeyboardButton(text=lang1[lang_user]['main_menu']['buttons']['settings']), types.KeyboardButton(text=lang1[lang_user]['main_menu']['buttons']['my_orders'])],
        [types.KeyboardButton(text=lang1[lang_user]['main_menu']['buttons']['about_us']), types.KeyboardButton(text=lang1[lang_user]['main_menu']['buttons']['feedback'])]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    print(4, user_data)
    await message.answer(f"{lang1[lang_user]['main_menu']['answer']}",
                         reply_markup=keyboard)


async def check_main_menu(message: types.Message):
    print(5, user_data)
    user_id = message.from_user.id
    lang_user=user_data[user_id]['lang']
    if message.text == lang1[lang_user]['main_menu']['buttons']['order']:
        await order(message)
    elif message.text == lang1[lang_user]['main_menu']['buttons']['settings']:
        pass
    elif message.text == lang1[lang_user]['main_menu']['buttons']['my_orders']:
        pass
    elif message.text == lang1[lang_user]['main_menu']['buttons']['about_us']:
        await about_us(message)
    elif message.text == lang1[lang_user]['main_menu']['buttons']['feedback']:
        pass
    # elif message.text == 'Yetkazib berish':
    #     user_data[user_id]['state'] = 'ask_location'
    #     await ask_location(message)
    # elif message.text == '':
    #     await back(message)
    # elif message.text == 'Olib ketish':
    #     pass
    # else:
    #     print(5, 'ohiri')
    #     await main_menu(message)


async def order(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['state'] = 'order'
    lang_user=user_data[user_id]['lang']
    print(6, user_data)
    buttons = [
        [types.KeyboardButton(text=lang1[lang_user]['order']['buttons']['take_away']), types.KeyboardButton(text=lang1[lang_user]['order']['buttons']['delivery'])],
        [types.KeyboardButton(text=lang1[lang_user]['back'])]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(lang1[lang_user]['order']['answer'], reply_markup=keyboard)

async def about_us(message:types.Message):
    user_id = message.from_user.id
    user_data[user_id]['state'] = 'about_us'
    lang_user=user_data[user_id]['lang']
    print(6.1, user_data)
    await message.answer(lang1[lang_user]['aboutus'])

async def check_order(message: types.Message):
    print(7, user_data)
    user_id = message.from_user.id
    lang_user=user_data[user_id]['lang']
    if message.text == lang1[lang_user]['order']['buttons']['delivery']:
        await ask_location(message)
    elif message.text == lang1[lang_user]['order']['buttons']['take_away']:
        await get_out(message)

async def get_out(message: types.Message):
    user_id = message.from_user.id
    print('get',user_data)
    filial = ["Yangi yo'l", "Yunusabad", "Maxim Gorkiy", "Boulevard", "Chilonzor", "Beruniy"]
    user_data['filial']=filial
    user_data[user_id]['state']='filial'
    lang_user=user_data[user_id]['lang']
    buttons = [[types.KeyboardButton(text="Orqaga"),types.KeyboardButton(text="Eng yaqin filialni aniqlash")]]
    for i in filial:
        button=[types.KeyboardButton(text=i)]
        buttons.append(button)
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(lang1[lang_user]['get_out']['answer'], reply_markup=keyboard)
    print('get',user_data)

async def check_get(message: types.Message):
    print(10, user_data)
    user_id = message.from_user.id
    lang_user=user_data[user_id]['lang']
    if message.text in user_data['filial']:
        print(True)
        await category_menu(message)
    else:
        print(message.text)
        await message.answer(lang1[lang_user]['check_get'])

async def ask_location(message: types.Message):
    user_id = message.from_user.id
    lang_user=user_data[user_id]['lang']
    user_data[user_id]['state'] = 'location'
    user_data[user_id]['location'] = ''
    print(8, user_data)

    user_id = message.from_user.id
    buttons = [
        [types.KeyboardButton(text=lang1[lang_user]['ask_location']['buttons'], request_location=True)],
        [types.KeyboardButton(text=lang1[lang_user]['back'])]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    await message.answer(lang1[lang_user]['ask_location']['answer'], reply_markup=keyboard)


async def address(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['state'] = 'get_location'
    lang_user=user_data[user_id]['lang']
    print(9, user_data)
    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude

        client = Client("363a3afc-06fc-4db8-80ad-dcff30c91d0b")
        location = client.address(Decimal(str(longitude)), Decimal(str(latitude)))
        user_data[user_id]['location'] = location
        buttons = [
            [types.KeyboardButton(text=lang1[lang_user]['address']['buttons']['resend']), types.KeyboardButton(text=lang1[lang_user]['address']['buttons']['ok'])],
            [types.KeyboardButton(text=lang1[lang_user]['address']['buttons']['save']), types.KeyboardButton(text=lang1[lang_user]['back'])],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(f"Address: {location}", reply_markup=keyboard)
        print(location)
    else:
        pass


menu = {
    'Burgerlar': {
        'Twins burger': {'description': 'Twins burger description', 'image': 'images/photo_2025-04-23_17-01-25.jpg', 'price': 39000},
        'Cheeseburger': {'description': 'Cheeseburger description', 'image': 'images/twins.jpg', 'price': 32000},
    },
    'Desertlar': {
        'Medovik': {'description': 'Medovik description', 'image': 'medovik.png', 'price': 14000},
        'Chocotastic': {'description': 'Chocotastic description', 'image': 'chocotastic.png', 'price': 15000},
    },

    'Ichimliklar': {
        'Ice-tea': {'description': 'Ice-tea description', 'image': 'ice-tea.png', 'price': 15000},
        'Sok': {'description': 'Sok description', 'image': 'sok.png', 'price': 23000},
    }
}


async def check_address(message: types.Message):
    print(10, user_data)
    user_id=message.from_user.id
    lang_user=user_data[user_id]['lang']
    if message.text == lang1[lang_user]['address']['buttons']['ok']:
        await category_menu(message)
    elif message.text == lang1[lang_user]['address']['buttons']['save']:
        pass
    elif message.text == lang1[lang_user]['back']:
        await back(message)


async def category_menu(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id]['state'] = 'category_menu'
    lang_user=user_data[user_id]['lang']
    buttons = [[types.KeyboardButton(text=lang1[lang_user]['back']), types.KeyboardButton(text=lang1[lang_user]['save'])]]
    for cat in menu:
        button = [types.KeyboardButton(text=cat)]
        buttons.append(button)

    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    print(11, user_data)
    await message.answer(lang1[lang_user]['category_menu'], reply_markup=keyboard)


async def check_category(message: types.Message):
    category = message.text
    user_id = message.from_user.id
    lang_user=user_data[user_id]['lang']
    if category in menu:
        user_data[user_id]['state'] = 'item_menu'
        user_data[user_id]['category'] = category
        buttons = [[types.KeyboardButton(text=lang1[lang_user]['back']), types.KeyboardButton(text=lang1[lang_user]['save'])]]
        for item in menu[category]:
            button = [types.KeyboardButton(text=item)]
            buttons.append(button)
        keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
        await message.answer(f"{category}\n"
                             f"{lang1[lang_user]['check_category']}", reply_markup=keyboard)
    print(12, user_data)


async def check_item(message: types.Message):
    user_id = message.from_user.id
    item = message.text
    category = user_data[user_id]['category']
    lang_user=user_data[user_id]['lang']
    if item in menu[category]:
        user_data[user_id]['item'] = item
        product = menu[category][item]
        description = product['description']
        price = product['price']
        image = product['image']
        temp_basket = {item: 1}
        user_data[user_id]['temp_basket'] = temp_basket
        caption = f"{item}\n" \
                  f"{description}\n" \
                  f"Narx: {price}"
        photo = types.FSInputFile(image)
        buttons = [
            [types.InlineKeyboardButton(text='-', callback_data='minus'),
             types.InlineKeyboardButton(text=str(1), callback_data='count'),
             types.InlineKeyboardButton(text='+', callback_data='plus')],
            [types.InlineKeyboardButton(text='Savatga qoshish', callback_data='add')]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer_photo(photo=photo, caption=caption, reply_markup=keyboard)
    print(13, user_data)


@dp.callback_query()
async def operations(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    action = callback.data
    item = user_data[user_id]['item']

    counter = user_data[user_id]['temp_basket'][item]
    lang_user=user_data[user_id]['lang']
    if action == 'minus':
        if counter > 1:
            user_data[user_id]['temp_basket'][item] -= 1
    elif action == 'plus':
        user_data[user_id]['temp_basket'][item] += 1
    elif action == 'add':
        if 'basket' not in user_data[user_id]:
            user_data[user_id]['basket'] = {}
        await add_basket(user_id, user_data[user_id]['temp_basket'])
        await callback.message.delete()
        await callback.message.answer(f"Savatga qo'shild")

    print('Counter:', user_data[user_id]['temp_basket'])
    print(14, user_data)
    category = user_data[user_id]['category']

    description = menu[category][item]['description']
    price = menu[category][item]['price']
    image = menu[category][item]['image']
    total_price = price * user_data[user_id]['temp_basket'][item]
    caption = f"{item}\n" \
              f"{description}\n" \
              f"Narx: {price}\n" \
              f"Umumiy narx: {total_price}"
    photo = types.InputMediaPhoto(
        media=types.FSInputFile(image),
        caption=caption
    )
    buttons = [
        [types.InlineKeyboardButton(text='-', callback_data='minus'),
         types.InlineKeyboardButton(text=str(user_data[user_id]['temp_basket'][item]), callback_data='count'),
         types.InlineKeyboardButton(text='+', callback_data='plus')],
        [types.InlineKeyboardButton(text='Savatga qoshish', callback_data='add')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        await callback.message.edit_media(media=photo, reply_markup=keyboard)
    except:
        pass


async def add_basket(user_id, temp_basket):
    lang_user=user_data[user_id]['lang']
    if 'basket' in user_data[user_id]:
        basket_dict = user_data[user_id]['basket']
        print('basket-dict 1',basket_dict)
        basket_dict.update(temp_basket)
        print('basket-dict 2',basket_dict)

    print(15, user_data)



async def main():
    await dp.start_polling(bot)


print('The bot is running...')
asyncio.run(main())