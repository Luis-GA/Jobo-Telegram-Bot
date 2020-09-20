#!/usr/bin/env python
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pymongo import MongoClient
from NEAS import NEAS


class JoboBot:
    bot = None
    db = None
    neas = None
    updater = None
    subscribed_users = []

    def __init__(self):
        # Env variables validation
        token = os.getenv('TOKEN')
        mongodb_url = os.getenv('MONGODB')
        jobo_user = os.getenv('JOBO_USER')
        jobo_password = os.getenv('JOBO_PASSWORD')

        if not (token and mongodb_url and jobo_user and jobo_password):
            raise Exception('Please set the following environment variables:\n'
                            '\t"TOKEN": With the token given by the @BotFather\n'
                            '\t"MONGODB": With the Connection String of Atlas MongoDB\n'
                            '\t"JOBO_USER": With your Jobo user account (email)\n'
                            '\t"JOBO_PASSWORD": With your Jobo password\n')

        # Assign Bot token
        self.updater = Updater(token, use_context=True)
        self.bot = self.updater.bot
        # Assign DB
        client = MongoClient(mongodb_url)
        self.db = client.jobot
        # Get Users
        for user in self.db.users.find():
            self.subscribed_users.append(int(user['user_id']))
        # Init Scrapping process
        self.neas = NEAS(bot=self.bot, db=self.db, jobo_auth=(jobo_user, jobo_password))

    def __start__(self, update, context):
        update.message.reply_text('Bienvenido al JoboBot!')

    def __echo__(self, update, context):
        if update.message:  # your bot can receive updates without messages
            # Reply to the message
            if update.message.text == 'ALL':
                self.neas.print_current_events(update.message.chat_id)
            elif update.message.text == 'SUB':
                if update.message.chat_id not in self.subscribed_users:
                    self.__subscribe_user__(update)

            elif update.message.text == 'UNSUB':
                self.__unsuscribe_user__(update)

    def __subscribe_user__(self, update):
        user_id = update.message.chat_id
        self.subscribed_users.append(user_id)
        user = {'user_id': user_id, 'first_name': update.message.chat.first_name}
        try:
            user['user_name'] = '@' + update.message.chat.username
        except Exception:
            pass

        self.db.users.insert_one(user)
        if len(list(self.db.historico_users.find({'user_id': user_id}))) == 0:
            self.db.historico_users.insert_one(user)
        update.message.reply_text(
            '{}, empiezas la suscripcion de alertas de Jobo'.format(update.message.chat.first_name))

    def __unsuscribe_user__(self, update):
        if update.message.chat_id in self.subscribed_users:
            update.message.reply_text(str('Te has dado de baja de las alertas de Jobo\n'
                                          'Esperamos verte pronto, {}'.format(update.message.chat.first_name)))
            self.subscribed_users.remove(update.message.chat_id)
            self.db.users.delete_many({'user_id': int(update.message.chat_id)})

    def run(self):

        dp = self.updater.dispatcher

        dp.add_handler(CommandHandler("start", self.__start__))

        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.__echo__))

        self.updater.start_polling()

        self.updater.idle()


if __name__ == '__main__':
    JoboBot().run()
