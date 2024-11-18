from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
import texts

button_make = KeyboardButton(texts.but_profile)
button_active = KeyboardButton('Купить VPN')
button_info = KeyboardButton(texts.but_info)
button_ref = KeyboardButton(texts.but_ref)

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(button_make,button_active).add(button_info).add(button_ref)

button_key = KeyboardButton('Мои ключи')
button_share = KeyboardButton(texts.but_menu)

profile_kb = ReplyKeyboardMarkup(resize_keyboard=True)
profile_kb.add(button_key).add(button_share)