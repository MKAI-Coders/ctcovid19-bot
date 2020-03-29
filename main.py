from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import logging
import config
import mysql.connector
import requests

import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Stages
NAMA, GENDER, USIA, AIMS, ALAMAT, FIRST, SECOND = range(7) #

# Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX = range(6)

global nama_user, gender_user, usia_user, aims_user, alamat_user

def db_write(user, kondisi):
        # Connect to server
    db = mysql.connector.connect(
        host=config.host,
        port=3306,
        database='ctcovid19',
        user=config.user,
        password=config.passwd)

    # Get a cursor
    cur = db.cursor()
    insert_query = "INSERT INTO user_short (id_telegram, username_telegram, nama_telegram, diagnosis) VALUES (%s, %s, %s, %s)"
    # Execute a query
    cur.execute(insert_query, (user.id, user.username, user.first_name, kondisi))
    
    db.commit()
    cur.close()
    db.close()

def start(update, context):    
    update.message.reply_text("Halo, saat ini Anda berbicara dengan *CleanTheCovid-19 Bot*. dibuat oleh *Komunitas CleanTheCity dan di support oleh beberapa dokter dari AMMA. Powered by MKA Indonesia*.\n\n*#CleanTheCovid19*\n\nBerikut layanan yang dapat anda akses, tekan tombol dibawah ini :\n\n/start - Perkenalan bot\n/deteksi - Konsul dokter & Test Mandiri COVID-19\n/info - Kabar terkini COVID-19 di Indonesia dan Dunia\n/cegah - Mencegah COVID-19", parse_mode=ParseMode.MARKDOWN)
    
def deteksi_(update, context):
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    
    logger.info("User %s started the conversation.", user.first_name)
    update.message.reply_text("Silakan isi data diri terlebih dahulu.\n\nSiapa *nama Anda* ?", parse_mode=ParseMode.MARKDOWN)    
    return NAMA

def deteksi_over(update, context):
    #global nama_user
    
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    user = query.message.chat
    # Get Bot from CallbackContext
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(ONE)),
         InlineKeyboardButton("Tidak", callback_data=str(FOUR))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = "Halo {},\nApakah dalam 3 hari terakhir Anda merasakan : \
        \n- gejala mirip masuk angin \
        \n- sakit tenggorokan ringan \
        \n- sedikit sakit (tidak demam, tidak lelah, masih makan dan minum secara normal) \
        \n\n*Tekan tombol dibawah ini :*".format(user.first_name),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return FIRST

def nama(update, context):
    global nama_user
    nama_user = update.message.text
    
    #print(update)
    
    reply_keyboard = [['Laki-laki', 'Perempuan']]
    
    update.message.reply_text("Apakah anda Laki-laki atau Perempuan?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))  

    return GENDER

def gender(update, context):
    global gender_user
    gender_user = update.message.text
    
    update.message.reply_text("Berapa *usia Anda* (tahun) ? ", reply_markup = ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)  
    
    return USIA

def usia(update, context):
    
    global usia_user
    usia_user = update.message.text
    
    update.message.reply_text("Berapa *nomor AIMS* Anda ?", parse_mode=ParseMode.MARKDOWN)  
    
    return AIMS

def aims(update, context):
    global aims_user
    
    aims_user = update.message.text
    
    update.message.reply_text("*Di mana Anda tinggal ?*\nketik dengan format berikut:\n\n*Provinsi/Kota/Kecamatan/Kelurahan atau Desa*", parse_mode=ParseMode.MARKDOWN)  
    
    return ALAMAT

# def alamat(update, context):
#     global alamat_user
#     alamat_user = update.message.text
    
#     reply_keyboard = [['Lanjut']]
    
#     update.message.reply_text("Terima kasih, data anda sudah terisi. selanjutnya kami akan melakukan assesment. Klik Lanjut.", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))  
    

#     return KONFIRM

def deteksi(update, context):
    user = update.message.from_user
    
    logger.info("Captured data : %s %s %s", user.id, user.username, user.first_name)
    
    keyboard = [
        [InlineKeyboardButton("Ya", callback_data=str(ONE)),
         InlineKeyboardButton("Tidak", callback_data=str(FOUR))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send message with text and appended InlineKeyboard
    update.message.reply_text(
        "Halo {},\nApakah dalam 3 hari terakhir Anda merasakan : \
        \n- gejala mirip masuk angin \
        \n- sakit tenggorokan ringan \
        \n- sedikit sakit (tidak demam, tidak lelah, masih makan dan minum secara normal) \
        \n\n*Tekan tombol dibawah ini :*".format(user.first_name),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST

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
        text =  "Pada hari ke 4, apakah Anda merasakan : \
                \n- sakit tenggorokan sedikit \
                \n- suara mulai serak \
                \n- suhu tubuh berkisar 36,5 C (kondisi ini tergantung orang) \
                \n- sakit kepala ringan \
                \n- diare ringan \
                \n\n*Tekan tombol dibawah ini :*",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
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
    
    user = query.message.chat
    db_write(user, "sakit")
    
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text = "*Anda Beresiko Tinggi (Pasien Dalam Pengawasan)!* \
                \n\nKarantina diri dan perlu pemeriksaan lanjutan ke RS rujukan COVID-19 \
                \n\nJangan panik, relawan dokter kami : [dr. Fatimah Rahmat](https://t.me/Fatimah_Rahmat) siap memberi arahan atau *Hubungi 119 EXT 9.* \
                \n\nKlik disini untuk konsultasi dengan dokter Fatimah : [@Fatimah_Rahmat](https://t.me/Fatimah_Rahmat)",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    # Transfer to conversation state `SECOND`
    return SECOND

def four(update, context):
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
        text="\nAnda berada di wilayah pandemi? atau kontak dengan pasien positif COVID-19 ? \
              \n\natau memiliki aktifitas harian: \
              \nsebagai pelayan publik (resepsionis, SPG, pegawai bank, dll) ? \
              \n\natau mobilitas tinggi (driver, ekspedisi, dll) ? \
              \n\n*Tekan tombol dibawah ini :*",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return FIRST

def six(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    
    user = query.message.chat
    db_write(user, "sehat")
    
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*Anda tidak perlu memeriksakan diri ke rumah sakit.* \
              \nJaga kesehatan diri anda dengan, makan makanan sehat, terhidrasi dengan baik, banyak minum dan istirahat yang cukup.\
              \n\nJaga Perilaku Hidup Bersih dan Sehat (PHBS) dan kesehatan tubuh. Istirahat jika kondisi tidak sehat, hindari keramaian, jaga jarak 1 meter dari orang di sekitar dan memakai masker jika terkena batuk dan pilek. \
              \n\nTingkatkan rasa syukur kepada Allah SWT karena sudah diberi kesehatan.",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    # Transfer to conversation state `SECOND`
    return SECOND

def five(update, context):
    """Show new choice of buttons"""
    query = update.callback_query
    
    user = query.message.chat
    db_write(user, "karantina")
    
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="*Anda Beresiko (Dalam Pengawasan)!* \
              \n\nKarantina diri anda selama 14 hari terhitung setelah kontak/kunjungan. \
              \n\nJaga kesehatan diri Anda dengan, makan makanan sehat, terhidrasi dengan baik, banyak minum dan istirahat yang cukup.  \
              \n\nJaga Perilaku Hidup Bersih dan Sehat (PHBS) dan kesehatan tubuh.    \
              \n\nTingkatkan rasa syukur kepada Allah SWT karena sudah diberi kesehatan. \
              \n\n*Bagaimana selama 14 hari karantina ?*  \
              \nJika dalam masa karantina atau setelahnya Anda merasakan :  \
              \n- gejala mirip masuk angin \
              \n- sakit tenggorokan ringan \
              \n- sedikit sakit (tidak demam, tidak lelah, masih makan dan minum secara normal) \
              \n\nAnda perlu pemeriksaan lanjut atau berkonsultasi via chatting dengan relawan dokter kami : [dr. Fatimah Rahmat](https://t.me/Fatimah_Rahmat) agar Anda tetap dalam pengawasan dokter.\n\nKlik disini untuk konsultasi dengan dokter Fatimah : [@Fatimah_Rahmat](https://t.me/Fatimah_Rahmat)",
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
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
        text="Semoga {} dan keluarga selalu sehat dan terlindung dari wabah COVID-19. Aamiin\n\nSilakan untuk mengakses menu lainnya:\n/info - Kabar terkini COVID-19 di Indonesia dan Dunia\n/cegah - Mencegah COVID-19".format(user_name)
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
    
    update.message.reply_text("*Kabar terkini COVID-19 di Indonesia* \
                              \n\nPositif: {}\nSembuh: {}\nMeninggal: {} \
                              \n\n*Kabar terkini COVID-19 di Dunia* \
                              \n\nPositif: {}\nSembuh: {}\nMeninggal: {} \
                              \n\nSumber: https://kawalcorona.com/".format(confirmed, recovered, deaths, confirmed_w, recovered_w, deaths_w ), parse_mode=ParseMode.MARKDOWN),

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
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('deteksi', deteksi)],
        states={
            # NAMA: [MessageHandler(Filters.text, nama)],
            
            # GENDER: [MessageHandler(Filters.text, gender)],
            
            # USIA: [MessageHandler(Filters.text, usia)],
            
            # AIMS: [MessageHandler(Filters.text, aims)],
            
            # ALAMAT: [MessageHandler(Filters.text, alamat)],
            
            FIRST: [CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                    CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                    CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                    CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                    CallbackQueryHandler(five, pattern='^' + str(FIVE) + '$'),
                    CallbackQueryHandler(six, pattern='^' + str(SIX) + '$')],
            
            SECOND: [CallbackQueryHandler(deteksi_over, pattern='^' + str(ONE) + '$'),  
                     CallbackQueryHandler(end, pattern='^' + str(TWO) + '$')]
        }
        ,fallbacks=[CommandHandler('deteksi', deteksi)]
    )

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