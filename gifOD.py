import json 
import time
import requests
import urllib
import telebot
from dbhelper import DBHelper 
from telebot import types
import random

TOKEN = '343952190:AAGS1Oa3KLjVOxOr1oBv-tGqWh3V9o4vPp4'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)
db = DBHelper()
bot = telebot.TeleBot(TOKEN)
GIF_KEY = 'dc6zaTOxFJmzC'
GIF_URL = 'http://api.giphy.com/v1/gifs/random?api_key='
LAST_TEXT = ''

gif_dialog = ['А вот и гифка дня!',
			'Гифки это круто! Держи',
			'Гифку? Нивапрос',
			'Graphics Interchange Format. Или просто гифка',
			'О вот хорошая',
			'Гифку дня в каждый дом!',
			'Гифка от giphy',
			'Держи гифку и никуда не уходи',
			'sudo apt-get gifka приди',
			'tic-tac-toe',
]
variants = ['well', 'scissors', 'sheet',]

def ttt_keyboard(chat_id):
	markup = types.ReplyKeyboardMarkup(row_width=2)
	btn_well = types.KeyboardButton('well')
	btn_scissors = types.KeyboardButton('scissors')
	btn_sheet = types.KeyboardButton('sheet')
	markup.row(btn_well)
	markup.row(btn_sheet)
	markup.row(btn_scissors)
	bot.send_message(chat_id, 'Выбери свой вариант', reply_markup=markup)

#generate and send gif
def send_gif(GIF_URL, GIF_KEY, chat_id):
	url = GIF_URL+GIF_KEY
	r = requests.get(url)
	jr = r.json()
	randGif = jr['data']['image_url']
	send_message(randGif, chat_id)

#downloads content from url and gives us a string
def get_url(url):
	response = requests.get(url)
	content = response.content.decode('utf8')
	return content

#parse url response into dictionary object
def get_json_from_url(url):
	content = get_url(url)
	js = json.loads(content)
	return js

#get updates of all messages 
def get_updates(offset=None):
	url = URL + 'getUpdates?timeout=100'
	#offset param indicate which message is latest so that older messages won't be uploaded
	if offset:
		url +='&offset={}'.format(offset)
		print(url)
	js = get_json_from_url(url)
	return js

def get_last_update_id(updates):
	update_ids = []
	for update in updates['result']:
		update_ids.append(int(update['update_id']))
	return max(update_ids)

#artificial tyoung effect delay can be from 25 to 75 accordingly to len of text
#text is string message
def typing_effect(delay, text, chat_id, keyboard=False):
	for i in range(delay):
		i = bot.send_chat_action(chat_id, 'typing')
	send_message(text, chat_id)

def ttt_intro(chat):
	typing_effect(15, 'Хочешь свою гифку?', chat)
	typing_effect(15, 'Тогда давай сыграем в игру', chat)
	typing_effect(15, 'Камень, ножницы, бумага', chat)

def tic_tac_toe(updates, chat, chat_id, variants, LAST_TEXT, text):
		ttt_intro(chat)
		ttt_keyboard(chat_id)
		text = ''
		last_update_id = None
		ai_choice = ''
		print('text after reset '+ text)
		while not text == 'well' or not text == 'scissors' or not text == 'sheet':
			ai_choice = random.choice(variants)
			print('ai ' + ai_choice)
			updates = get_updates(last_update_id)
			if len (updates['result'])>0:
				last_update_id = get_last_update_id(updates)+1
			for update in updates['result']:
				text = update['message']['text']
				print('text before check '+ text)
			if text == 'well' or text == 'scissors' or text == 'sheet':
				break
		db.add_item(text, chat)
		print('text ' + text)
		if ai_choice == 'sheet' and text == 'scissors':
			typing_effect(15, ai_choice, chat)
			typing_effect(15, 'Ты выиграл', chat)
			typing_effect(15, 'Вот твоя награда', chat)
			send_gif(GIF_URL, GIF_KEY, chat)
		elif ai_choice == 'well' and text == 'scissors':
			typing_effect(15, ai_choice, chat)
			typing_effect(15, 'Ты проиграл', chat)
		elif ai_choice == 'sheet' and text == 'well':
			typing_effect(15, ai_choice, chat)
			typing_effect(15, 'Ты проиграл', chat)
		elif ai_choice == 'scissors' and text == 'sheet':
			typing_effect(15, ai_choice, chat)
			typing_effect(15, 'Ты проиграл', chat)
		elif ai_choice == 'scissors' and text == 'well':
			typing_effect(15, ai_choice, chat)
			typing_effect(15, 'Ты выиграл', chat)
			typing_effect(15, 'Вот твоя награда', chat)
			send_gif(GIF_URL, GIF_KEY, chat)
		elif ai_choice == 'well' and text == 'sheet':
			typing_effect(15, ai_choice, chat)
			typing_effect(15, 'Ты выиграл', chat)
			typing_effect(15, 'Вот твоя награда', chat)
			send_gif(GIF_URL, GIF_KEY, chat)

def handle_updates(updates):
	for update in updates['result']:
		text = update['message']['text']
		chat = update['message']['chat']['id']
		chat_id = update['message']['chat']['id']
		if text == 'gif':
			db.add_item(text, chat)
			dialog = random.choice(gif_dialog)
			if dialog == 'tic-tac-toe':
				db.add_item(text, chat)
				tic_tac_toe(updates, chat, chat_id, variants, LAST_TEXT, text)
			else:
				typing_effect(15, dialog, chat)
				send_gif(GIF_URL, GIF_KEY, chat)
		elif text =='ttt':
			tic_tac_toe(updates, chat, chat_id, variants, LAST_TEXT, text)
#get only last chat message instead of all
def get_last_chat_id_and_text(updates):
	num_updates = len(updates['result'])
	last_update = num_updates-1
	text = updates['result'][last_update]['message']['text']
	chat_id = updates['result'][last_update]['message']['chat']['id']
	return (text, chat_id)

#sending message
def send_message(text, chat_id, reply_markup=None):
	text = urllib.parse.quote_plus(text)
	url = URL + 'sendMessage?text={}&chat_id={}&parse_mode=Markdown'.format(text, chat_id)
	if reply_markup:
		url += '&reply_markup={}'.format(reply_markup)
	get_url(url)

def main():
	db.setup()
	last_update_id = 823337300
	while True:
		updates = get_updates(last_update_id)
		if len (updates['result'])>0:
			last_update_id = get_last_update_id(updates)+1
			print('last update id' + str(last_update_id))
			handle_updates(updates)
		time.sleep(0.5)

if __name__ == '__main__':
	main()
