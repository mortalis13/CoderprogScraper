import time
import io

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
    print(f"\n---------last_message---------\n'''\n{last_message}\n'''\n")
    
    lines = last_message.split('\n')
    for line in lines:
      if line.startswith('https'):
        last_link = line.strip()
        break

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
    text = f'{item.title}\n{item.link}\n{item.date}\n\n- - - - - - - - - - - - - - - - - -\n'
    
    # Workaround from https://github.com/LonamiWebs/Telethon/issues/1473
    image_wrapper = io.BytesIO(item.image)
    image_wrapper.name = 'post.png'
    bot.send_file(CHANNEL_CHAT_ID, image_wrapper, caption=text)
    
    print(f'Message sent for "{item.title}"')
    sent += 1
    time.sleep(1)
  
  print(f'\nSent {sent} messages\n')
  

main()
