#!/bin/env python3
Ver=0.2

from config import API_KEY,YOUTUBE_LINK_REGEX

# telegram library 
from src.library import telegram , CallbackQueryHandler
from src.main import video , audio , getinfo , gethelp , videoHandler

import logging
# logging bot output
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

def main():
    "Run the bot."

    updater = telegram.ext.Updater(API_KEY,use_context= True)
    disp  = updater.dispatcher

    disp.add_handler(telegram.ext.CommandHandler('video',video,pass_args= True))
    disp.add_handler(telegram.ext.CommandHandler('audio',audio,pass_args= True))
    disp.add_handler(telegram.ext.CommandHandler('info',getinfo,pass_args= True))
    disp.add_handler(telegram.ext.CommandHandler('help',gethelp))
    updater.dispatcher.add_handler(CallbackQueryHandler(videoHandler))

    updater.start_polling(timeout=30)
    updater.idle()

if __name__ == '__main__':
    main()