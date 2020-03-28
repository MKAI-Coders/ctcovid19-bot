#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple inline keyboard bot with multiple CallbackQueryHandlers.
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import logging
import config
#import urllib2

import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Stages
NAMA, FIRST, SECOND = range(3)

# Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX = range(6)

def start(update, context):
    update.message.reply_text("Hallo, saat ini anda berbicara dengan Clean The Covid-19 Bot. Dibuat oleh Komunitas Clean the City di support oleh beberapa dokter dari AMMA. Powered by MKA Indonesia.\n\nBerikut layanan yang dapat anda akses, tekan tombol dibawah ini:\n\n/deteksi - Deteksi gejala infeksi COVID-19\n/info - Kabar terkini COVID-19 di Indonesia dan Dunia\n/cegah - Mencegah COVID-19")

def deteksi(update, context):
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    
    logger.info("User %s started the conversation.", user.first_name)
    update.message.reply_text("Silakan mengisi data terlebih dahulu.\nMasukkan nama anda")    
    return NAMA

# def deteksi_over(update, context):
#     keyboard = [
#         [InlineKeyboardButton("Ya", callback_data=str(ONE)),
#          InlineKeyboardButton("Tidak", callback_data=str(TWO))]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
    
#     # Send message with text and appended InlineKeyboard
#     update.message.reply_text(
#         "Apakah kamu pernah kontak dengan pasien positif COVID-19 (berada dalam satu ruangan yang sama/kontak dalam jarak 1 meter) ATAU pernah berkunjung ke negara/daerah Endemis COVID-19 dalam 14 hari terakhir",
#         reply_markup=reply_markup
#     )
#     # Tell ConversationHandler that we're in state `FIRST` now
#     return FIRST

def deteksi_over(update, context):
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # Get Bot from CallbackContext
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(ONE)),
         InlineKeyboardButton("Tidak", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Apakah kamu pernah kontak dengan pasien positif COVID-19 (berada dalam satu ruangan yang sama/kontak dalam jarak 1 meter) ATAU pernah berkunjung ke negara/daerah Endemis COVID-19 dalam 14 hari terakhir",
        reply_markup=reply_markup
    )
    return FIRST

def nama(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(ONE)),
         InlineKeyboardButton("Tidak", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(
        "Apakah kamu pernah kontak dengan pasien positif COVID-19 (berada dalam satu ruangan yang sama/kontak dalam jarak 1 meter) ATAU pernah berkunjung ke negara/daerah Endemis COVID-19 dalam 14 hari terakhir",
        reply_markup=reply_markup
    )
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST

# def one(update, context):
#     """Send message on `/start`."""
#     # Get user that sent /start and log his name
#     # user = update.message.from_user
#     # logger.info("User %s started the conversation.", user.first_name)
    
#     # Build InlineKeyboard where each button has a displayed text
#     # and a string as callback_data
#     # The keyboard is a list of button rows, where each row is in turn
#     # a list (hence `[[...]]`).
#     keyboard = [
#         [InlineKeyboardButton("Ya", callback_data=str(ONE)),
#          InlineKeyboardButton("Tidak", callback_data=str(TWO))]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
    
#     # Send message with text and appended InlineKeyboard
#     update.message.reply_text(
#         "Apakah kamu pernah kontak dengan pasien positif COVID-19 (berada dalam satu ruangan yang sama/kontak dalam jarak 1 meter) ATAU pernah berkunjung ke negara/daerah Endemis COVID-19 dalam 14 hari terakhir",
#         reply_markup=reply_markup
#     )
#     # Tell ConversationHandler that we're in state `FIRST` now
#     return FIRST

# def deteksi_over(update, context):
#     """Prompt same text & keyboard as `start` does but not as new message"""
#     # Get CallbackQuery from Update
#     query = update.callback_query
#     # Get Bot from CallbackContext
#     bot = context.bot
#     keyboard = [
#         [InlineKeyboardButton("Ya", callback_data=str(ONE)),
#          InlineKeyboardButton("Tidak", callback_data=str(TWO))]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     # Instead of sending a new message, edit the message that
#     # originated the CallbackQuery. This gives the feeling of an
#     # interactive menu.
#     bot.edit_message_text(
#         chat_id=query.message.chat_id,
#         message_id=query.message.message_id,
#         text="Pernah kontak dengan pasien positif COVID-19 (berada dalam satu ruangan yang sama/kontak dalam jarak 1 meter) ATAU pernah berkunjung ke negara/daerah Endemis COVID-19 dalam 14 hari terakhir",
#         reply_markup=reply_markup
#     )
#     return FIRST

# Kalo Ya
def one(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(THREE)),
         InlineKeyboardButton("Tidak", callback_data=str(FOUR))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
      
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Sedang atau pernah mengalami :\n1. demam (>38 C)\n2. pilek\n3. batuk\n4. sesak napas",
        reply_markup=reply_markup
    )
    return FIRST

# kalo Tidak
def two(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(FIVE)),
         InlineKeyboardButton("Tidak", callback_data=str(SIX))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text= "Sedang atau pernah mengalami :\n1. demam (>38 C)\n2. pilek\n3. batuk\n4. sesak napas",
        reply_markup=reply_markup
    )
    return FIRST

def three(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Hubungi dokter atau periksakan diri ke rumah sakit rujukan COVID-19 di daerah Anda",
        reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return SECOND

def four(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(THREE)),
         InlineKeyboardButton("Tidak", callback_data=str(SIX))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Karantina diri Anda selama 14 hari terhitung setelah kontak/kunjungan\n\nApakah selama 14 hari karantina diri Anda mengalami : \n1. demam (>38 C)\n2. pilek\n3. batuk\n4. sesak napas",
        reply_markup=reply_markup
    )
    return FIRST

def five(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Periksakan diri ke dokter terdekat dan istirahat yang cukup",
        reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return SECOND

def six(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Anda tidak perlu memeriksakan diri ke rumah sakit. Selalu jaga kesehatan Anda",
        reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return SECOND

def end(update, context):
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    query = update.callback_query
    bot = context.bot
    
    user_name = query.message.chat.first_name
    #update.message.from_user  'username': 'spdin', 'first_name': 'Saripudin'
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="Semoga {} dan keluarga selalu sehat dan terlindung dari wabah COVID-19. Aamiin".format(user_name)
    )
    
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def info(update, context):

    r = requests.get('https://api.kawalcorona.com/indonesia/')
    
    confirmed = r.json()[0]['positif']
    recovered = r.json()[0]['sembuh']
    deaths = r.json()[0]['meninggal']
    
    r = requests.get('https://api.kawalcorona.com/positif/')
    confirmed_w = r.json()['value']
    
    r = requests.get('https://api.kawalcorona.com/sembuh/')
    recovered_w = r.json()['value']
    
    r = requests.get('https://api.kawalcorona.com/meninggal/')
    deaths_w = r.json()['value']
    
    update.message.reply_text("Kabar terkini COVID-19 di Indonesia \
                              \n\nPositif: {}\nSembuh: {}\nMeninggal: {} \
                              \n\n\nKabar terkini COVID-19 di Dunia \
                              \n\nPositif: {}\nSembuh: {}\nMeninggal: {} \
                              \n\nSumber: https://kawalcorona.com/".format(confirmed, recovered, deaths, confirmed_w, recovered_w, deaths_w ))

def cegah(update, context):
    bot = context.bot
    bot.send_photo(chat_id=update.message.chat_id, photo=open('img/cucitangan.jpeg', 'rb'))
     
def about(update, context):
    update.message.reply_text("Bot untuk mengecek kesehatan dan konsultasi dokter dari gejala infeksi virus COVID-19. Sesuai dengan petunjuk Kemenkes. Powered by AMMA. Support By MKAI.\n\n/start - Deteksi gejala infeksi COVID-19\n/info - Kabar terkini COVID-19 di Indonesia\n/help - Cara mencuci tangan")
    

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    
    #dp.add_handler(CommandHandler("start", start))
    #dp.add_handler(CallbackQueryHandler(deteksi, pattern='deteksi'))
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('deteksi', deteksi)],
        states={
            NAMA: [MessageHandler(Filters.text, nama)],
            
            FIRST: [CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                    CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                    CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                    CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                    CallbackQueryHandler(five, pattern='^' + str(FIVE) + '$'),
                    CallbackQueryHandler(six, pattern='^' + str(SIX) + '$')],
            
            SECOND: [CallbackQueryHandler(deteksi_over, pattern='^' + str(ONE) + '$'),  
                     CallbackQueryHandler(end, pattern='^' + str(TWO) + '$')]
        },
        
        fallbacks=[CommandHandler('deteksi', deteksi)]
    )

    # Add ConversationHandler to dispatcher that will be used for handling
    # updates
    dp.add_handler(conv_handler)
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("deteksi", deteksi))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("cegah", cegah))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()