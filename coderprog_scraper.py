import datetime
from dataclasses import dataclass

import seleniumbase
import pyquery

# pip install -U seleniumbase pyquery
# seleniumbase 4.28.5
# seleniumbase 4.30.3
# seleniumbase 4.32.4
# seleniumbase 4.32.12

HOST = 'https://coderprog.com'
MAX_RETRIES = 3
POST_DATA = []


@dataclass
class Entry:
  title: str
  link: str
  date: datetime.date
  type: str
  image: bytes

class WrongPageSource(Exception): pass

class Finish(Exception): pass

class ErrorExit(Exception): pass

class RetryParsing(Exception): pass


def process_error_source(html):
  print('Parsing error page')
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


def get_image(selenium, url):
  selenium.uc_open_with_reconnect(url, 2)
    
  image = selenium.find_element("img")
  data = image.screenshot_as_png
  return data


def process_page(selenium, last_link):
  html = selenium.driver.page_source
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
    
    type_ = ''

    full_post = post.find('.full-post')
    if full_post:
      text = full_post.text()
      is_pdf = 'PDF' in text
      is_epub = 'EPUB' in text
      is_video = not is_pdf and not is_pdf
      
      if is_video:
        print('[ Found video, skipping ]\n')
        continue
      
      types = []
      if is_pdf:
        types.append('PDF')
      if is_epub:
        types.append('EPUB')
      type_ = ', '.join(types)

    stop_process = False
    if last_link:
      stop_process = link == last_link or link == last_link + '/'

    else:
      stop_process = POST_DATA and POST_DATA[0].date != date

    if stop_process:
      print(f'\n-----------------------\nStop entry found: {date}, {link}\n---------------\n')
      return True

    image = get_image(selenium, image)
    POST_DATA.append(Entry(title, link, date, type_, image))

  return False


def process(selenium, last_link):
  end_reached = False
  page = 1
  retries = 0
  
  while not end_reached:
    url = f'https://coderprog.com/page/{page}'
    print(f'Page {url}\n')

    selenium.uc_open_with_reconnect(url, 4)
    selenium.uc_gui_handle_captcha()  # Tab + Space
    # selenium.uc_gui_click_captcha()  # Mouse click
    
    try:
      end_reached = process_page(selenium, last_link)
    
    except RetryParsing:
      retries += 1
      if retries > MAX_RETRIES:
        print('Retries exceeded max. Ending.')
        raise Finish()
      continue
      
    print('Parsing done')
    page += 1
    retries = 0
    
    print()

  print(f' ______\n|\n|Found {len(POST_DATA)} entries after the last posted\n|\n ‾‾‾‾‾‾')


def run(last_link: str | None) -> list[Entry]:
  try:
    with seleniumbase.SB(uc=True) as selenium:
      try:
        process(selenium, last_link)

      except WrongPageSource: pass
      except Finish: pass
      except KeyboardInterrupt:
        print('Requested stop')
        raise
  
    return POST_DATA
  
  except KeyboardInterrupt:
    return None


if __name__ == '__main__':
  data = run(None)
  if not data: exit()

  with open('data_dump.json', 'w') as f:
    for item in data:
      f.write(f'{item.title} {item.link} {item.date} {item.type}\n')
