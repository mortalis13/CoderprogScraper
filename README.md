Gets data from the `Cloudflare` protected blog `coderprog.com` and posts messages to a private `Telegram` channel.

## Configuration
To connect to `Telegram API`:
Go to https://my.telegram.org -> Login -> API Development tools -> Create new application -> Get API ID and hash and save them in `main.py`

Create a Telegram bot with the `BotFather` bot and save the token in `main.py`.  
(The bot is optional but is needed to send messages to the private chat so the notification is generated and so the bubble with the number of unread messages can be seen)

Create a private chat, open it from a web browser and get its ID from the URL.  
Or use the `GetIDs Bot`.  
Save the chat ID to `CHANNEL_CHAT_ID` in `main.py`.

## Usage
Preferably use from a venv to avoid conflicts and independently update the core libraries
- Run on every usage `pip install -U seleniumbase`, to have the latest version, that would have the updated handling of Cloudflare captchas/restrictions
- `python main.py`
- Check the pages are being parsed and the data is sent to Telegram after that
- On the next run the script would take the latest entry saved and would start the parsing from that entry
- Remove `headless='new'` parameter if a page cannot be parsed (check the `page_dump.html` for errors), and resolve the captcha manually if needed
