from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import time as time_module
import dict
from datetime import datetime, time, timedelta
import requests
from urllib.parse import quote
import re
from selenium.common.exceptions import NoSuchWindowException
from openai import OpenAI
import zlib
import json
import traceback
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller
import pandas as pd
import matplotlib.pyplot as plt
import io
import seaborn as sns
import os


def shortSite(tickers_str) :
    stock_url = f"https://finviz.com/quote.ashx?t={tickers_str}&p=d#statements"
                                
    response = requests.get(stock_url, headers = headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', 'js-snapshot-table snapshot-table2 screener_snapshot-table-body')

    # StringIO를 사용하여 pandas가 HTML 테이블을 DataFrame으로 변환할 수 있도록 준비
    table_html = str(table)
    table_io = io.StringIO(table_html)
    df = pd.read_html(table_io)[0]

    sns.set_style("darkgrid", {"axes.facecolor": "#0e1117", "grid.color": "gray", "text.color": "white"})
    plt.figure(figsize=(12, 2))  # Adjusted for demonstration, actual figsize would be based on content
    ax = plt.gca()
    ax.set_facecolor('#0e1117')
    ax.axis('tight')
    ax.axis('off')
    plt.axis('off')

    # Creating the table inside the plot without the header row and with alternating column colors
    the_table = plt.table(cellText=df.values, colLabels=None, loc='center', cellLoc='right')
    the_table.auto_set_font_size(False)
    the_table.scale(1.5, 1.5)  # Scale table size to make it more readable

    # Improve the appearance of the table
    the_table.set_fontsize(12)
    the_table.auto_set_column_width(col=list(range(len(df.columns))))  # Adjust the columns width

    # Alternating column colors
    cols = the_table.get_celld()
    for i in range(len(df.columns)):
        for j in range(len(df)):
            cell = cols[(j, i)]
            if i % 2 == 0:
                cell.set_fontsize(11)
                cell.set_facecolor('#121417')
            else:
                cell.set_facecolor('#464646')
            if i == 8 or i == 9:
                if j in [2, 3, 4]:  # These are the row indices for 'Short Float', 'Short Ratio', 'Short Interest'
                    if i == 8 :
                        cell.set_facecolor('#6060a2')
                    else :
                        cell.set_facecolor('#7a7acb')
                    cell.get_text().set_weight('bold')  # Make the text bold

            cell.set_edgecolor('white')


    # Save the plot as an image file
    image_path = 'table_image.png'
    plt.savefig(image_path, bbox_inches='tight', transparent=True)
    plt.close()

def deleteImage() :
    file_path = 'table_image.png'

    # 파일이 존재하는지 확인
    if os.path.exists(file_path):
        # 파일이 존재하면 삭제
        return True
    else:
        # 파일이 존재하지 않으면 메시지 출력
        return False

def unescape_html(text):
    replacements = {
        "&amp;": "&",
        "&quot;": '"',
        "&apos;": "'",
        "&gt;": ">",
        "&lt;": "<",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

OPENAI_API_KEY = ""
client = OpenAI(api_key=OPENAI_API_KEY)
def chat_gpt(ticker, airticle, cnt) :
    if cnt == 1:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 주식전문가입니다.",
                },
                {
                    "role": "user",
                    "content": f"\'{airticle}\'은 {ticker}에 관한 기사인데 어떤 뜻인지 요약해주고, 앞으로의 주가 전망에 대해 알려줘(대답에 기사를 한번더 쓰면 안됩니다.) 답변의 형식은 1.요약 2.주가전망 으로 해줘",
                },
            ],
        )
        return completion.choices[0].message.content
    else :
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 주식전문가입니다.",
                },
                {
                    "role": "user",
                    "content": f"\'{airticle}\'은 {ticker}들 에 관한 기사인데 어떤 뜻인지 요약해주고, 앞으로의 주가 전망에 대해 알려줘(대답에 기사를 한번더 쓰면 안됩니다.) 답변의 형식은 1.요약 2.주가전망 으로 해줘",
                },
            ],
        )
        return completion.choices[0].message.content

def send_telegram_message(message):
    api_key = ''
    chat_id = ''

    encoded_message = quote(message)  # 메시지를 URL 인코딩
    send_text = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&parse_mode=HTML&text={encoded_message}'
    response = requests.get(send_text)
    return response.json()

def send_telegram_photo(photo_path, message):
    api_key = ''
    chat_id = ''
    url = f'https://api.telegram.org/bot{api_key}/sendPhoto'
    
    # 파일을 'photo' 파라미터에 첨부
    files = {'photo': open(photo_path, 'rb')}
    # encoded_message = quote(message)  # 메시지를 URL 인코딩
    # 선택적으로, 캡션을 추가할 수 있습니다.
    data = {'chat_id': chat_id, 'caption': message, 'parse_mode': 'HTML'}
    
    # POST 요청으로 이미지 전송
    response = requests.post(url, files=files, data=data)
    return response.json()

def is_within_time_period(current, start, end):
    """현재 시간이 주어진 시간 범위 내에 있는지 확인합니다."""
    return start <= current <= end

def start_browser():
    user_agent = "Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36"
    options = {
        'proxy': {
            'http': 'socks5://127.0.0.1:9050',  # Tor 서비스의 HTTP 프록시 설정
            'https': 'socks5://127.0.0.1:9050',  # Tor 서비스의 HTTPS 프록시 설정
            'no_proxy': 'localhost,127.0.0.1'  # 프록시를 사용하지 않을 주소 목록
        }
    }

    chrome_options = Options()
    chrome_options.add_argument('user-agent=' + user_agent)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=1400,1500")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')

    browser = webdriver.Chrome(seleniumwire_options=options, options=chrome_options)
    # browser = webdriver.Chrome(options=chrome_options)

    return browser

def renew_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password='123456789')  # Tor ControlPort 패스워드를 사용하여 인증
        controller.signal(Signal.NEWNYM)
        time_module.sleep(controller.get_newnym_wait())  # Tor에서 새로운 경로를 준비하는 데 필요한 시간을 기다림

def start_stockTitan():
    user_agent = "Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36"
    options = Options()
    
    options.add_argument('user-agent=' + user_agent)
    options.add_argument("--headless")
    options.add_argument("window-size=1400,2000")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--lang=ko')  # 번역 언어를 한국어로 설정합니다.
    # 번역 기능을 사용할 때 필요한 번역 스크립트 URL을 추가합니다.
    options.add_argument("--translate-script-url=https://translate.googleapis.com/translate_static/js/element/main.js")
    
    # 요청을 차단할 규칙 정의
    def interceptor(request):
        if request.url.startswith('https://ad.'):
            request.abort()
        if request.url.startswith('https://ads.'):
            request.abort()
            
    # Selenium Wire 옵션 설정
    seleniumwire_options = {
        'request_interceptor': interceptor
    }
    stock_titan = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
    
    return stock_titan


def login(browser):
    bearer = ""
    login_url = "https://newsfilter.io/login"
    browser.get(login_url)
    WebDriverWait(browser, 30).until(
        lambda b: any('/login' in request.url for request in b.requests)
    )
    username_input = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, 'sign-up-email'))
    )
    password_input = WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, 'sign-up-password'))
    )
    username_input.send_keys('')
    password_input.send_keys('')
    
    # 로그인 버튼 요소를 찾습니다.
    parent_div = browser.find_element(By.CSS_SELECTOR, "div.sc-kpOJdX.hppIUc")
    # 부모 요소 내에서 로그인 버튼을 찾습니다.
    login_button = parent_div.find_element(By.CSS_SELECTOR, "button.sc-kGXeez.clIfze")
    login_button.click()

    # 로그인 후 userinfo 요청이 나타날 때까지 대기
    WebDriverWait(browser, 30).until(
        lambda b: any('/userinfo' in request.url for request in b.requests)
    )

    # userinfo 요청에서 Authorization 헤더 추출
    for request in browser.requests:
        if '/userinfo' in request.url:
            bearer = request.headers['Authorization']
            break

    time_module.sleep(3)
    
    return bearer

def action_response(browser) :
        # 'https://api.newsfilter.io/actions' 엔드포인트에 대한 'POST' 요청이 완료될 때까지 대기
    WebDriverWait(browser, 30).until(
        lambda b: any(request.method == 'POST' and request.url == 'https://api.newsfilter.io/actions' and request.response for request in b.requests)
    )
    
    # 정확한 URL을 가진 'POST' 요청에서 Authorization 헤더 추출
    for request in browser.requests:
        if request.method == 'POST' and request.url == 'https://api.newsfilter.io/actions':
            encoding = request.response.headers.get('Content-Encoding', '')

            # 압축된 내용일 경우 압축 해제
            if encoding == 'gzip':
                response_body_as_bytes = zlib.decompress(request.response.body, 16+zlib.MAX_WBITS)
            elif encoding == 'deflate':
                response_body_as_bytes = zlib.decompress(request.response.body)
            else:
                response_body_as_bytes = request.response.body

            # 바이트를 문자열로 디코딩
            response_body_as_string = response_body_as_bytes.decode('utf-8')
            # 문자열을 JSON 객체로 변환
            response_data = json.loads(response_body_as_string)
            # "articles" 키에 해당하는 값만 추출
            articles = response_data["articles"]
            # print(articles[0]['title'])
            
            filtered_articles = [
                article for article in articles
                if any(symbol for symbol in article.get('symbols', []) if symbol) or (article.get("details", {}).get("type") == "SC 13G")
            ]
            return filtered_articles
        
def elapsed_time() :
    current_time = time_module.time()
    elapsed_time = current_time - start_time

    # 경과 시간을 시, 분, 초 단위로 계산
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60

    # 조건에 따라 다른 문자열 생성
    if hours > 0:
        elapsed_time_str = f"{int(hours)}시간 {int(minutes)}분 {int(seconds)}초"
    elif minutes > 0:
        elapsed_time_str = f"{int(minutes)}분 {int(seconds)}초"
    else:
        elapsed_time_str = f"{int(seconds)}초"

    # 문자열을 사용하여 경과 시간 출력
    time_message = f"경과 시간: {elapsed_time_str}"
    return time_message

good = dict.good
bad = dict.bad
investors = dict.investors

# 모든 키워드를 한 딕셔너리로 결합
all_keywords = {**good, **bad}

browser = start_browser()
bearer = login(browser)

url = "https://newsfilter.io/latest/news/"
browser.get(url)

old_tickers = {}

alert_list = {} # 알림 보냈던 티커,점수

# 초기화 상태를 추적하기 위한 변수 추가
initialization_done_for_date = None
printed_for_first_period_date = None
printed_for_second_period_date = None

# 재시도 필요 상태를 추적하는 변수
retry_needed = False
headers = {'User-Agent' : 'Mozilla/5.0 (Linux; Android 9; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.83 Mobile Safari/537.36'}

start_time = time_module.time()
while(True) :
    try:
        if retry_needed:
            if browser is not None:
                browser.quit()
            time_module.sleep(15)  # 브라우저가 완전히 종료되기를 기다립니다.
            renew_tor_ip()
            browser = start_browser()  # 브라우저를 재시작합니다.
            bearer = login(browser)  # 필요한 경우, 로그인 과정을 다시 수행합니다.
            browser.get(url)  # 이전에 실패한 URL을 다시 시도합니다.
            retry_needed = False  # 재시도 상태를 리셋합니다.
            
        new_tickers = {}
        # 페이지가 로드되고 특정 요소가 클릭 가능해질 때까지 기다립니다.
        # 이는 페이지가 충분히 로드되었다는 것을 나타내는 하나의 지표로 사용됩니다.
        
        articles = action_response(browser)
        for article in articles:
            if 'details' in article and article['details'].get('type') == 'SC 13G':
                title = article['title']
                title_lower = title.lower()
                description = article['description']
                article_url = article['sourceUrl']
                article_id = article['id']
                if article_id not in old_tickers :
                    for investor in investors:
                        investor_lower = re.escape(investor).lower()
                        if re.search(r'\b' + investor_lower + r'\b', title_lower):
                            response = requests.get(article_url, headers = headers)
                            html = response.text
                            soup = BeautifulSoup(html, 'html.parser')
                            def find_inc_tag(tag):
                                return tag.name in ["p", "b"] and tag.get_text(strip=True).endswith("Inc.")

                            company = soup.find(find_inc_tag)

                            if company:
                                company_text = company.get_text(strip=True).replace('\n', ' ')
                                message = (
                                    f"🟢🟢지분 공시 알림🟢🟢\n\n"
                                    f"회사명: {company_text}\n\n"
                                    f"투자자: {investor}\n\n"
                                    f"{article_url}"
                                )
                                # print(message)
                                send_telegram_message(message)
                                # print(message)
                                new_tickers[article_id] = 10
                        
                            break 
                        
            else :
                symbols = article['symbols']
                title = article['title']
                description = article['title']
                article_url = article['url']
                article_id = article['id']
                
                article_lower = title.lower()
                keyword = ""
                score = 0
                for a, b in good.items():
                    a_lower = a.lower()
                    
                    if re.search(r'\b' + re.escape(a_lower) + r'\b', article_lower):
                        keyword = a
                        score = b
                        break
                    
                if keyword != "":
                    result_string = ""
                    if len(symbols)>0 :
                        tickers_str = ", ".join(symbols)
                            
                        if article_id not in old_tickers and alert_list.get(tickers_str, 0) < score :    
                            stock = False
                            if ',' not in tickers_str and article_id not in old_tickers:
                                # stockTitan = start_stockTitan()  # 브라우저를 재시작합니다.
                                
                                stock_url = f"https://www.stocktitan.net/news/{tickers_str}/"
                                
                                response = requests.get(stock_url, headers = headers)
                                html = response.text
                                soup = BeautifulSoup(html, 'html.parser')
                                # print(soup)
                                # stockTitan.get(stock_url)
                                # stockTitan.execute_script("""
                                # var iframes = document.querySelectorAll('iframe');
                                # iframes.forEach(function(iframe) { iframe.remove(); });
                                # """)
                                # stockTitan.execute_script("""
                                # var iframes = document.querySelectorAll('div.adv');
                                # iframes.forEach(function(iframe) { iframe.remove(); });
                                # """)
                                # WebDriverWait(stockTitan, 30).until(
                                #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div.news-feed-content'))
                                # )
                                title_element = soup.find('a', 'text-gray-dark')
                                if title_element is not None:
                                    if title_element.get_text() == unescape_html(title) :
                                        
                                        element = soup.find('div', 'companies-card-summary')
                                        description = element.get_text()
                                        description = description.replace("Rhea-AI Summary", "").strip().replace("\n", "")
                                        
                                        # target_div = stockTitan.find_element(By.CSS_SELECTOR, 'div.news-feed-content')
                                        # location = target_div.location
                                        # size = target_div.size

                                        # # 특정 div를 스크린샷으로 캡처
                                        # stockTitan.save_screenshot('screenshot.png')

                                        # # div의 위치와 크기에 따라 이미지를 잘라냄
                                        # left = location['x']
                                        # top = location['y']
                                        # right = left + size['width']
                                        # bottom = top + size['height']

                                        # # 스크린샷에서 div 부분만 잘라내어 저장
                                        # from PIL import Image
                                        # img = Image.open('screenshot.png')
                                        # img = img.crop((left, top, right, bottom))
                                        # img.save('div_image.png')
                                        # 텔레그램으로 이미지 전송
                                        # 웹 드라이버 종료
                                        stock = True
                                    
                                    article_data = soup.find('div', class_='article-data')

                                    panels = article_data.find_all('div', class_='article-data-panel')

                                    infos = panels[2].find_all('div', class_='news-list-item')

                                    # 출력 내용을 저장할 빈 문자열을 초기화합니다.
                                    

                                    border_length = 36  # 여백을 줄인 테두리 길이

                                    # 시작하는 테두리를 문자열에 추가합니다.
                                    result_string += "+" + "-" * border_length + "+\n"

                                    cnt = 0
                                    # 각 항목에 대해 루프를 돌며 내용을 추출하고 출력합니다.
                                    for index, item in enumerate(infos):
                                        # 'label' 태그의 텍스트를 추출합니다.
                                        label = item.find('label').text.strip()
                                        # 같은 'div' 내에서 'span' 태그를 찾아 그 텍스트를 추출합니다.
                                        if label.upper() == "INDUSTRY" or label.upper()  == "WEBSITE" or label.upper()  == "CITY" or label.upper()  == "SHORT PERCENT" or label.upper()  == "FLOAT":
                                            continue
                                        else:
                                            value = item.find('span').text.strip()
                                            cnt+=1
                                            # 만약 현재 항목이 마지막이면 \n을 한 번만 추가합니다.
                                            if index == len(infos) - 1:
                                                formatted_text = f"{cnt}. {label} : {value}\n"
                                            else:
                                                formatted_text = f"{cnt}. {label} : {value}\n"
                                            result_string += formatted_text

                                    # 마무리 테두리를 문자열에 추가합니다.
                                    result_string += "+" + "-" * border_length + "+\n"

                                
                                shortSite(tickers_str)
                                    
                                # stockTitan.quit()
                                          
                            # 메시지를 구성
                            gpt = chat_gpt(tickers_str, description, len(symbols))
                            article_url = '<a href="'+article_url+'">기사 링크</a>'
                            # gpt = ""
                            message = (
                                f"🟢🟢 {tickers_str} 🟢🟢\n\n원본: {title}\n\nKeyword: {keyword}\n\nScore: {score}\n\n------ GPT 분석 ------\n{gpt}\n{result_string}{article_url}"
                            )
                            
                            # send_telegram_message(message)
                   
                            if deleteImage :
                                send_telegram_photo('table_image.png', message)
                                os.remove('table_image.png')
                            else :
                                send_telegram_message(message)
                            alert_list[tickers_str] = score

                        elif tickers_str in alert_list and score == -1:
                            del alert_list[tickers_str] 
                            message = (
                                f"🔴🔴 {tickers_str} 🔴🔴\n\n원본 : {title}\n\nKeyword : {keyword}\n\nScore: {score} 악재"
                            )
                            send_telegram_message(message)
                            
                        new_tickers[article_id] = score
                        

                                        
                
        old_tickers = new_tickers

        now = datetime.now()
        current_time = now.time()
        current_date = now.date()

        # 시간 비교 후 대기 시간 설정
        #  wait_time = 30 if is_within_time_period(current_time, time(3, 30), time(17, 30)) else 40
        wait_time = 60 if is_within_time_period(current_time, time(3, 30), time(14, 30)) else 40
        
        # 오전 8시부터 9시까지 초기화
        if is_within_time_period(current_time, time(8, 0), time(9, 0)):
            if initialization_done_for_date != current_date:
                # 기존 크롬 세션 종료
                browser.quit()
                messages = []
                yesterday_date = current_date - timedelta(days=1)
                messages.append(f"🟢🟢 {yesterday_date} 의 호재 확인 🟢🟢")
                sorted_alert_list = sorted(alert_list.items(), key=lambda item: item[1], reverse=True)
                for ticker, score in sorted_alert_list:
                    messages.append(f"🟢 {ticker} : {score}")
                message = "\n".join(messages)  # 모든 메시지를 하나의 문자열로 결합
                send_telegram_message(message)
                browser.quit()
                time_module.sleep(20)
                # 새 크롬 세션 시작
                browser = start_browser()   
                # 로그인
                bearer = login(browser)
                
                old_tickers = {}
                alert_list = {}
                initialization_done_for_date = current_date

        # 오후 5시 50분부터 5시 55분 사이에 alert_list 출력
        if is_within_time_period(current_time, time(16, 50), time(16, 55)):
            if printed_for_first_period_date != current_date:
                messages = []
                messages.append("🟢🟢 프장 전 호재 확인 🟢🟢")
                sorted_alert_list = sorted(alert_list.items(), key=lambda item: item[1], reverse=True)
                for ticker, score in sorted_alert_list:
                    messages.append(f"🟢 {ticker} : {score}")
                message = "\n".join(messages)  # 모든 메시지를 하나의 문자열로 결합
                send_telegram_message(message)
                printed_for_first_period_date = current_date

        # 밤 11시 20분부터 11시 25분 사이에 alert_list 출력
        if is_within_time_period(current_time, time(22, 20), time(22, 25)):
            if printed_for_second_period_date != current_date:
                messages = []
                messages.append("🟢🟢 본장 전 호재 확인 🟢🟢")
                sorted_alert_list = sorted(alert_list.items(), key=lambda item: item[1], reverse=True)
                for ticker, score in sorted_alert_list:
                    messages.append(f"🟢 {ticker} : {score}")
                message = "\n".join(messages)  # 모든 메시지를 하나의 문자열로 결합
                send_telegram_message(message)
                printed_for_second_period_date = current_date

        # 대기 시간 설정 및 sleep
        a = random.randrange(wait_time, wait_time + 4)
        # a = 10
        

        browser.quit()
        time_module.sleep(a/2)
        browser = start_browser()
        login(browser)
        browser.get(url)
        
        # time_message = elapsed_time()
        # send_telegram_message(time_message)
        
        time_module.sleep(a/2)
        
    except NoSuchWindowException:
       # send_telegram_message("브라우저 재시작")
        # 브라우저 재시작 로직
        
        traceback.print_exc()
        retry_needed = True
        continue
    
    except Exception as e:
        #send_telegram_message("브라우저 재시작")
        # 브라우저 재시작 로직
        
        traceback.print_exc()
        retry_needed = True
        continue
    
