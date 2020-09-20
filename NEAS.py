import sched
import time
from threading import Thread
from scraping import JoboScraping


class NEAS:
    s = sched.scheduler(time.time, time.sleep)
    current_events = None
    new_events = None
    db_client = None
    bot = None
    scrap = None
    no_image = 'https://xerolighting.com/wp-content/uploads/2018/06/noimage.jpg'
    refresh_minutes = 1

    def __init__(self, bot, db, jobo_auth):
        self.bot = bot
        self.db_client = db
        self.scrap = JoboScraping(jobo_auth=jobo_auth)
        past_events = list(self.db_client.events.find())
        self.current_events = []
        if len(past_events) != 0:
            for event in past_events:
                self.current_events.append(event['title'])

        Thread(target=self.search_new_events).start()

    def __print_events__(self, user_id, events):
        for event in events:
            string = "🎭Titulo: " + str(event['title']) + \
                     "\n🗺Lugar: " + str(event['place']) + \
                     "\n📆Dias: " + str(event['days']) + \
                     "\n🔗Link: " + str(event['link'])
            if event['image'] != 'none':
                self.bot.send_photo(chat_id=user_id, photo=event['image'], caption=string)
            else:
                self.bot.send_photo(chat_id=user_id, photo=self.no_image, caption=string)

    def __alerting_task__(self, events_difference):
        alerts = []
        for event in events_difference:
            alerts.append(self.new_events[event])
            self.current_events.append(event)

        for user in self.db_client.users.find():
            user_id = user['user_id']
            self.__print_events__(user_id, alerts)

    def __update_db__(self):
        self.db_client.events.drop()
        for key in self.new_events.keys():
            self.db_client.events.insert_one(self.new_events[key])

    def search_new_events(self):
        self.new_events = self.scrap.get_list_of_events()
        if self.new_events.get('scraping_error'):
            events_difference = []
        else:
            events_difference = set(self.new_events.keys()) - set(self.current_events)
            self.__update_db__()

        if len(events_difference) != 0:
            self.__alerting_task__(events_difference)

        self.s.enter(60 * self.refresh_minutes, 1, self.search_new_events)
        self.s.run()

    def print_current_events(self, user_id):
        events = list(self.db_client.events.find())
        self.__print_events__(user_id, events)
