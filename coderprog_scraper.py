import time
import datetime
from dataclasses import dataclass

import seleniumbase
import selenium_stealth

import pyquery

# pip install seleniumbase selenium-stealth pyquery

POST_DATA = []

@dataclass
class Entry:
  title: str
  link: str
  date: datetime.date

class WrongPageSource(Exception):
  pass


def init():
  user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.140 Safari/537.36"
  driver = seleniumbase.Driver(uc=True, headless='new', agent=user_agent)
  selenium_stealth.stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
  )
  return driver

def finish(driver):
  if not driver:
    return
  driver.quit()


def process_error_source(html):
  print('Prasing error page')
  with open('page_dump.html', 'w') as f:
    f.write(html)

  doc = pyquery.PyQuery(html)
  text = doc.find('#cf-error-details span.inline-block')
  code = doc.find('#cf-error-details span.code-label')
  if text and code:
    print(f'{text.text()} ({code.text()})')
  else:
    print('Error text not parsed. Check the page_dump.html.')


def process_page(html, last_link):
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

    print(f'title: {title}, link: {link}, date {date}')

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

    POST_DATA.append(Entry(title, link, date))

  return False


def process(driver, last_link):
  end_reached = False
  page = 1

  while not end_reached:
    url = f'https://coderprog.com/page/{page}'
    print(f'Page {url}\n')

    driver.get(url)
    time.sleep(20)

    end_reached = process_page(driver.page_source, last_link)
    print('Parsing done')
    page += 1
    if not end_reached:
      time.sleep(2)
    print()

  print(f' ______\n| Found {len(POST_DATA)} entries\n ‾‾‾‾‾‾')


def run(last_link: str | None) -> list[Entry]:
  driver = init()

  try:
    process(driver, last_link)
  except WrongPageSource:
    pass

  finish(driver)

  return POST_DATA


if __name__ == '__main__':
  run(None)
