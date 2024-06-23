import time
import datetime
from dataclasses import dataclass

import seleniumbase
import selenium_stealth

import pyquery

# pip install seleniumbase selenium-stealth pyquery

HOST = 'https://coderprog.com'
MAX_RETRIES = 3
POST_DATA = []

@dataclass
class Entry:
  title: str
  link: str
  date: datetime.date
  image: bytes

class WrongPageSource(Exception):
  pass

class Finish(Exception):
  pass

class RetryParsing(Exception):
  pass


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36"


def process_error_source(html):
  print('Prasing error page')
  with open('page_dump.html', 'w') as f:
    f.write(html)

  if 'Waiting for coderprog.com to respond' in html:
    print('Could not complete verification in time. Retying.')
    raise RetryParsing()
    
  doc = pyquery.PyQuery(html)
  error_text = doc.find('#cf-error-details span.inline-block')
  error_code = doc.find('#cf-error-details span.code-label')
  if error_text and error_code:
    print(f'{error_text.text()} ({error_code.text()})')
  else:
    print('Error text not parsed. Check the page_dump.html.')


def get_image(sb, url):
  sb.open(url)
  time.sleep(6)
  
  image = sb.find_element("img")
  data = image.screenshot_as_png
  return data

def process_page(sb, last_link):
  html = sb.driver.page_source
  doc = pyquery.PyQuery(html)
  posts = doc('.latestPost')
  posts = list(posts.items())

  print(f'Found {len(posts)} posts\n')
  if not posts:
    process_error_source(html)
    raise WrongPageSource()

  for post in posts:
    header = post.find('.title a')
    title = header.text().strip()
    link = header.attr.href
    date = post.find('.post-info .date').text().strip()
    date = datetime.datetime.strptime(date, '%B %d, %Y').date()
    image = HOST + post.find('img').attr.src

    print(f'title: {title}, link: {link}, date {date}, image {image}')

    full_post = post.find('.full-post')
    if full_post:
      text = full_post.text().lower()
      is_video = 'pdf' not in text and 'epub' not in text
      if is_video:
        print('[ Found video, skipping ]')
        continue

    stop_process = False
    if last_link:
      stop_process = link == last_link or link == last_link + '/'

    else:
      stop_process = POST_DATA and POST_DATA[0].date != date

    if stop_process:
      print(f'\n-----------------------\nStop entry found: {date}, {link}\n---------------\n')
      return True

    image = get_image(sb, image)
    POST_DATA.append(Entry(title, link, date, image))

  return False


def process(sb, last_link):
  end_reached = False
  page = 1
  retries = 0

  while not end_reached:
    url = f'https://coderprog.com/page/{page}'
    print(f'Page {url}\n')

    sb.open(url)
    time.sleep(10)
    
    try:
      end_reached = process_page(sb, last_link)
    
    except RetryParsing:
      retries += 1
      if retries > MAX_RETRIES:
        print('Retries exceeded max. Ending.')
        raise Finish()
      continue
      
    print('Parsing done')
    page += 1
    retries = 0
    
    if not end_reached:
      time.sleep(2)
    print()

  print(f' ______\n|\n|Found {len(POST_DATA)} entries after the last posted\n|\n ‾‾‾‾‾‾')


def run(last_link: str | None) -> list[Entry]:
  with seleniumbase.SB(uc=True, headless='new', agent=user_agent) as sb:
    try:
      process(sb, last_link)
    except WrongPageSource:
      pass
    except Finish:
      pass

    return POST_DATA


if __name__ == '__main__':
  run(None)
