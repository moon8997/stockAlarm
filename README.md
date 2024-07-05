# stockAlarm
![upload1](https://github.com/moon8997/stockAlarm/assets/67020351/c3964fcf-9761-44c8-bd3a-88f3759fc115)

# 프로젝트 설명
이 프로젝트는 Selenium을 사용하여 주식 관련 웹사이트에서 정보를 수집하고, 특정 키워드를 포함하는 기사를 분석하여 주식 심볼과 관련된 정보를 수집한 후, OpenAI의 GPT 모델을 사용하여 기사를 요약하고 주가 전망을 예측하여 Telegram으로 알림을 보내는 프로그램입니다.


# 주요 라이브러리 및 모듈
selenium: 웹 브라우저를 자동화하기 위해 사용.

requests: 웹 요청을 보내고 응답을 받기 위해 사용.

BeautifulSoup: HTML을 파싱하여 데이터를 추출하기 위해 사용.

OpenAI: OpenAI API를 사용하여 GPT 모델을 활용.

pandas: 데이터 처리를 위해 사용.

matplotlib 및 seaborn: 데이터 시각화를 위해 사용.

stem: Tor 네트워크를 제어하기 위해 사용.

urllib.parse: URL 인코딩을 위해 사용.

json: JSON 데이터를 다루기 위해 사용.

# 주요 함수 및 로직 설명
shortSite: Finviz 웹사이트에서 주식 정보를 수집하고 데이터프레임으로 변환한 후, 이를 시각화하여 이미지 파일로 저장.

deleteImage: 저장된 이미지 파일을 삭제.

unescape_html: HTML 엔티티를 일반 텍스트로 변환.

OpenAI GPT 모델 사용

chat_gpt: OpenAI GPT 모델을 사용하여 기사를 요약하고 주가 전망을 예측.

Telegram 메시지 전송

send_telegram_message: Telegram으로 텍스트 메시지를 전송.

send_telegram_photo: Telegram으로 사진과 함께 메시지를 전송.

Selenium 웹 브라우저 설정 및 제어

start_browser: Selenium을 사용하여 웹 브라우저를 시작하고 설정.

renew_tor_ip: Tor 네트워크의 IP 주소를 갱신.

start_stockTitan: Stock Titan 웹사이트에서 데이터를 수집하기 위한 브라우저 설정.

login: 웹사이트에 로그인하고 필요한 인증 정보를 추출.

action_response: 웹사이트에서 기사를 수집하고 필요한 정보를 추출.

기타 유틸리티 함수

is_within_time_period: 현재 시간이 주어진 시간 범위 내에 있는지 확인.

elapsed_time: 프로그램 시작 이후 경과 시간을 계산.

# 메인 로직
브라우저 시작 및 로그인: start_browser와 login 함수를 사용하여 브라우저를 시작하고 로그인.

기사 수집 및 분석: action_response 함수를 사용하여 기사를 수집하고, 특정 조건에 맞는 기사를 분석.

Telegram 알림 전송: 수집된 기사 정보를 바탕으로 Telegram 메시지와 사진을 전송.

시간 기반 초기화 및 알림: 특정 시간대에 초기화 작업을 수행하고, 알림 리스트를 출력.

재시도 로직: 오류 발생 시 브라우저를 재시작하고 작업을 재시도.

# 코드의 흐름
브라우저 시작 및 로그인:

start_browser와 login 함수를 통해 Selenium 브라우저를 시작하고 로그인.

기사 수집 및 분석:

action_response 함수를 사용하여 뉴스 기사를 수집하고 분석.

특정 키워드와 일치하는 기사를 필터링하고, chat_gpt 함수를 통해 기사를 요약하고 주가 전망을 예측.

Telegram 알림 전송:

send_telegram_message와 send_telegram_photo 함수를 사용하여 Telegram 메시지와 이미지를 전송.

주기적인 초기화 및 재시도:

특정 시간대에 브라우저를 초기화하고, 주요 정보를 다시 수집.

오류 발생 시 브라우저를 재시작하고 작업을 재시도.

# 실행 방법

필요한 라이브러리를 설치합니다.

OpenAI API 키와 Telegram API 키를 설정합니다.

프로그램을 실행하여 브라우저를 시작하고 로그인합니다.

뉴스 기사를 주기적으로 수집하고 분석하여 Telegram으로 알림을 보냅니다.
