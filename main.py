import time

from telethon import TelegramClient, events, sync

import coderprog_scraper as scraper

# pip install telethon


CHANNEL_CHAT_ID = -1001111111111
BOT_TOKEN = ''

API_ID = 0
API_HASH = ''


client = TelegramClient('client_session', API_ID, API_HASH).start()
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


def find_last_link():
  print('Getting the last posted link')
  messages = client.get_messages(CHANNEL_CHAT_ID, 1)

  last_link = None
  if messages and messages[0].message:
    last_message = messages[0].message
    print(f'\n---------last_message---------\n{last_message}\n-------------------\n')
    parts = last_message.split('\n')
    if len(parts) == 3:
      last_link = parts[1]

  print(f'last_link: {last_link}')
  return last_link


def main():
  last_link = find_last_link()

  if last_link:
    print(f'\nStart getting data until the last processed entry with link: {last_link}\n')
  else:
    print(f'\nStart getting data for the last available day\n')

  data = scraper.run(last_link)
  if not data:
    return

  print('\nStart sending posts\n')
  sent = 0

  for item in reversed(data):
    text = f'{item.title}\n{item.link}\n{item.date}'
    bot.send_message(CHANNEL_CHAT_ID, text)
    print(f'Message sent for "{item.title}"')
    sent += 1
    time.sleep(1)

  print(f'\nAll messages sent, total {sent}\n')


main()
