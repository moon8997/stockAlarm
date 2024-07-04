import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote  # URL 인코딩을 위해 추가
from datetime import datetime

global time_volume

def send_telegram_message(message):
    api_key = ''
    chat_id = ''

    encoded_message = quote(message)  # 메시지 전체를 URL 인코딩

    send_text = f'https://api.telegram.org/bot{api_key}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={encoded_message}'

    response = requests.get(send_text)
    return response.json()

def format_volume(volume):
    if volume >= 1000000:  # 백만 단위 이상인 경우
        return f"{volume / 1000000:.2f}M"
    elif volume >= 1000:  # 천 단위 이상인 경우
        return f"{volume / 1000:.2f}K"
    else:  # 천 단위 미만인 경우
        return str(volume)

def format_gainers_message(gainers):
    messages = []
    current_message = ""
    for name, chg, volume, index in gainers:
        formatted_volume = format_volume(volume)
        new_line = f"Ticker: {name} ({chg}), Volume: {formatted_volume}\n"
        if len(current_message) + len(new_line) > 4096:  # 메시지 길이 체크
            messages.append(current_message)
            current_message = new_line
        else:
            current_message += new_line
    messages.append(current_message)  # 마지막 메시지 추가
    return messages

def decrease_and_cleanup_send_list():
    global send_list
    send_list = [(name, count - 1) for name, count in send_list if count > 1]
    # 카운트다운이 1 이하로 내려가면 리스트에서 제거

def is_allowed_to_send(name):
    return not any(item for item in send_list if item[0] == name)

# 웹 페이지 URL
# 사용자 입력 받기
# user_choice = input("1 : 5min \n2 : pre \n")
# # 입력에 따라 URL 결정
# if user_choice == '2':
#     url = 'https://www.webull.com/quote/us/gainers/pre'
#     time_volume = 100000
# elif user_choice == '1':
#     url = 'https://www.webull.com/quote/us/gainers/5min'
#     time_volume = 1000000
# else:
#     print("Invalid choice. Defaulting to 'pre'.")
#     url = 'https://www.webull.com/quote/us/gainers/5min'

# print(f"Selected URL: {url}")


old_top_gainer = []
send_list = []

is_first_loop = True

decrease_and_cleanup_send_list()

org_url = ""

while True:
    now = datetime.now()
    current_time = now.time()

    if now.weekday() != 6:

        if current_time >= datetime.strptime('23:30', '%H:%M').time() or current_time <= datetime.strptime('16:00', '%H:%M').time():
            url = 'https://www.webull.com/quote/us/gainers/5min'
            time_volume = 700000
        else:
            url = 'https://www.webull.com/quote/us/gainers/pre'
            time_volume = 100000

        if org_url != url :
            is_first_loop = True

        org_url = url

        response = requests.get(url)
        html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        rowss = soup.find_all(class_="table-row table-row-hover")[:15]

        now_top_gainer = []
        for index, rows in enumerate(rowss):
            name_child = rows.contents[1]
            name_elements = name_child.select('.detail .txt')[0]
            name = name_elements.text

            chg_child = rows.contents[3]
            chg_elements = chg_child.select('span')[0]
            chg = chg_elements.text

            volume_child = rows.contents[7]
            volume_elements = volume_child.select('span')[0]
            volume = volume_elements.text

            if 'K' in volume:
                volume = float(volume.replace('K', '')) * 1000
            elif 'M' in volume:
                volume = float(volume.replace('M', '')) * 1000000
            else:
                volume = float(volume)
            
            now_top_gainer.append((name, chg, volume, index)) 


        if not is_first_loop:
            for item in now_top_gainer:
                name, chg, volume, current_index = item # chg 추출
                if name not in [old_name for old_name, _, _, _ in old_top_gainer] and volume >= time_volume and is_allowed_to_send(name):
                    formatted_volume = format_volume(volume) 
                    search_url = f'https://newsfilter.io/search?query=title:%22{name}%22%20OR%20description:%22{name}%22%20OR%20symbols:%22{name}%22'
                    send_telegram_message(f"Ticker : {name} ({chg}) \nVolume : {formatted_volume} \n{search_url}")
                    # print(f"Ticker : {name} ({chg}) \nVolume : {formatted_volume} \n{search_url}")
                    # send_telegram_message(search_url)
                    send_list.append((name, 30))

            for old_name, old_chg, old_volume, old_index in old_top_gainer:
                for name, chg, volume, current_index in now_top_gainer:
                    if name == old_name and abs(current_index - old_index) >= 2 and volume >= time_volume and chg > old_chg:
                        if current_index < old_index and is_allowed_to_send(name) :
                            formatted_volume = format_volume(volume) 
                            search_url = f'https://newsfilter.io/search?query=title:%22{name}%22%20OR%20description:%22{name}%22%20OR%20symbols:%22{name}%22'
                            send_telegram_message(f"Ticker : {name} ({chg}) \nVolume : {formatted_volume} \n{old_index + 1} > {current_index + 1}\n{search_url}")
                            send_list.append((name, 30))
            
            for item in now_top_gainer:
                name, chg, volume, current_index = item
                # 이전 정보 찾기
                prev_data = next((x for x in old_top_gainer if x[0] == name), None)
                if prev_data:
                    prev_volume = prev_data[2]
                    # volume 증가율 계산
                    increase_rate = (volume - prev_volume) / prev_volume * 100
                    # 25% 이상 증가했는지 확인
                    if increase_rate >= 15 and is_allowed_to_send(name) and volume >= time_volume :
                        formatted_volume = format_volume(volume)
                        formatted_increase_rate = f"{increase_rate:.2f}"
                        search_url = f'https://newsfilter.io/search?query=title:%22{name}%22%20OR%20description:%22{name}%22%20OR%20symbols:%22{name}%22'
                        # print(f"Ticker : {name} ({chg}) \nVolume : {formatted_volume} \n거래량 {formatted_increase_rate}% 증가! \n{search_url}")
                        send_telegram_message(f"Ticker : {name} ({chg}) \nVolume : {formatted_volume} \n거래량 {formatted_increase_rate}% 증가! \n{search_url}")
                        send_list.append((name, 30))
        else:
            is_first_loop = False
            
        # old_top_gainer 업데이트
        old_top_gainer = now_top_gainer.copy()
        decrease_and_cleanup_send_list()
        
        # if "463" in test_html:
        #     test_html = test_html.replace("463", "855")

        # elif "855" in test_html:
        #     test_html = test_html.replace("855", "463")

    time.sleep(30)

