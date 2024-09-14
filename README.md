Gets data from the Cloudflare protected blog coderprog.com and posts messages to a private Telegram channel.

To connect to Telegram API:

Go to https://my.telegram.org -> login -> API Development tools -> Create new application.
Get API ID and API hash.

Create a bot with BotFather bot from Telegram and get the bot token.
(The bot is optional but is needed to send messages to the private chat so the notification is generated and so the bubble with the number of unread messages can be seen)

Create a private chat, open it from a web browser and get its ID from the URL.
Paste the ID as numeric value in the code.

**Notes**
- using seleniumbase 4.28.5+ for handling Cloudflare captchas, the browser has to be opened in window mode and focused so the captcha can be clicked (only on the first page load)
- when executed after fresh install of selenium, if the first time the captcha is not handled, try to re-run the script, as PyAutoGUI installs some dependencies in runtime
