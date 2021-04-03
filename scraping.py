from requests import Session
from bs4 import BeautifulSoup as bs
import re


class JoboScraping:
    user = None
    password = None
    token = None
    session = Session()
    base_url = 'https://madridcultura-jobo.shop.secutix.com/'
    events_url = base_url + 'secured/list/events'
    login_url = base_url + 'account/login'
    link_re = '^/secured/selection/event/date?'

    def __init__(self, user=None, password=None, jobo_auth=None):
        if jobo_auth:
            self.user = jobo_auth[0]
            self.password = jobo_auth[1]
        else:
            self.user = user
            self.password = password

    def __decode_strings__(self, string):
        string = string.encode('ascii').decode('unicode-escape').encode('iso-8859-1').decode('utf-8')
        return string.replace('\r\n', '').replace('  ', '')

    def __clean_date__(self, string):
        string = string.replace('\\r', '').replace('range', '').replace('from', '').replace('to', '').replace('\\t', '')
        string = string.replace('\\n', '').replace('<', '').replace('>', '').replace('span', '').replace('unique', '')
        string = string.replace('class', '').replace('date', '').replace('=', '').replace('"', '')
        string = string.replace('day', '').replace('/', '').replace('time', '').replace('separator', '')
        return self.__decode_strings__(string.replace('separar', ' '))

    def __session_login__(self):

        try:
            if not self.token:
                site = self.session.get(self.login_url)
                bs_content = bs(site.content, 'html.parser')
                self.token = bs_content.find('input', {'name': '_csrf'})['value']

            login_data = {'login': self.user, 'password': self.password, '_csrf': self.token}
            self.session.post('https://madridcultura-jobo.shop.secutix.com/account/login', login_data)
        except Exception as e:
            print(e)
            self.token = None
            self.__session_login__()

    def __event_data_downloader__(self):
        events_home_page = bs(str(self.session.get(self.events_url).content), 'html.parser')

        event_name = events_home_page.find_all(attrs={'class': 'title'})[4:-10]
        event_image = events_home_page.find_all(attrs={'class': 'product_image_container product-image-scale-1'})
        days = events_home_page.find_all('span', class_='date')
        sites = events_home_page.find_all('span', class_='location')
        links = events_home_page.findAll('a', attrs={'href': re.compile(self.link_re), 'class': ['title']})

        return event_name, event_image, days, sites, links

    def __scrap_available_events__(self, event_name, event_image, days, sites, links):
        events = {}
        counter = 0
        counter_link = 0
        for event in event_name:
            if str(event).find('span') == 1:
                counter = counter + 1
                continue
            try:
                title = self.__decode_strings__(str(event.contents[0]))
                image = event_image[counter].contents[1][list(event_image[1].contents[1].attrs.keys())[10]]
                day = self.__clean_date__(str(days[counter_link]))
                place = self.__decode_strings__(sites[(counter * 2)].find('span', class_='site').get_text())
                try:
                    link = self.base_url[:-1] + links[counter_link].get('href', ' ')
                except:
                    link = 'https://madridcultura-jobo.shop.secutix.com/secured/list/events'
            except Exception as e:
                events['scraping_error'] = True
            counter = counter + 1
            counter_link = counter_link + 1
            if str(place) not in ('none', 'None'):
                try:
                    if not events.get(title):
                        events[title] = {'title': title, 'image': image, 'place': place, 'link': link, 'days': day}
                except Exception:
                    events[title] = {'title': title, 'image': image, 'place': place, 'link': link, 'days': day}
            else:
                events['scraping_error'] = True

        return events

    def get_list_of_events(self):

        # New Session builder
        self.__session_login__()
        # Download events
        event_name, event_image, days, sites, links = self.__event_data_downloader__()

        # Scrap events
        return self.__scrap_available_events__(event_name, event_image, days, sites, links)
