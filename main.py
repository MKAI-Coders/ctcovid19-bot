from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
import logging
import config
import mysql.connector
import requests
import re

import json

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Stages
NAMA, REINPUT_NAMA, GENDER, USIA, AIMS, CABANG, FIRST, SECOND, THIRD = range(9) #

# Callback data
ONE, TWO, THREE, FOUR, FIVE, SIX = range(6)

user_dict = {}

class User:
    def __init__(self, name):
        self.nama = name
        self.gender = None
        self.usia = None
        self.aims = None
        self.cabang = None

def db_load():
    db = mysql.connector.connect(
        host=config.host,
        port=3306,
        database='ctcovid19',
        user=config.user,
        password=config.passwd)
    
    cur = db.cursor()
    
    insert_query = "SELECT * FROM user_diagnosis WHERE id IN (SELECT MAX(id) FROM user_diagnosis GROUP BY id_telegram)"
    
    # Execute a query
    cur.execute(insert_query)
    
    records = cur.fetchall()
    
    for row in records:
        chat_id = int(row[2])
        
        print("loaded chat_id {}".format(chat_id))
        
        nama = row[5]
        aims = row[6]
        gender = row[7]
        usia = row[8]
        cabang = row[9]
        
        user = User(nama)
        user_dict[chat_id] = user
        
        user_data = user_dict[chat_id]
        user_data.usia = usia
        user_data.aims = aims
        user_data.gender = gender
        user_data.cabang = cabang
    
    db.commit()
    cur.close()
    db.close()
    
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
    insert_query = "INSERT INTO user_activity (id_telegram, username_telegram, nama_telegram, diagnosis) VALUES (%s, %s, %s, %s)"
    # Execute a query
    cur.execute(insert_query, (user.id, user.username, user.first_name, kondisi))
    
    db.commit()
    cur.close()
    db.close()

def db_write_diagnosis(user_tele, user, kondisi):
        # Connect to server
    db = mysql.connector.connect(
        host=config.host,
        port=3306,
        database='ctcovid19',
        user=config.user,
        password=config.passwd)

    # Get a cursor
    cur = db.cursor()
    insert_query = "INSERT INTO user_diagnosis (id_telegram, username_telegram, nama_telegram, nama, aims, gender, usia, cabang, diagnosis) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    # Execute a query
    cur.execute(insert_query, (user_tele.id, user_tele.username, user_tele.first_name, user.nama, user.aims, user.gender, user.usia, user.cabang, kondisi))
    
    db.commit()
    cur.close()
    db.close()

def start(update, context):  
    user = update.message.from_user
    
    logger.info("User %s started the conversation.", user.first_name)
    
    db_write(user, "start")
    
    update.message.reply_text("Halo, saat ini Anda berbicara dengan *CleanTheCovid-19 Bot*. dibuat oleh *Komunitas CleanTheCity dan di support oleh beberapa dokter dari AMMA. Powered by MKA Indonesia*.\n\n*#CleanTheCovid19*\n\nBerikut layanan yang dapat anda akses, tekan tombol dibawah ini :\n\n/start - Perkenalan bot\n/deteksi - Konsul dokter & Test Mandiri COVID-19\n/info - Kabar terkini COVID-19 di Indonesia dan Dunia\n/cegah - Mencegah COVID-19", parse_mode=ParseMode.MARKDOWN)
    
def deteksi(update, context):
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    
    db_write(user, "deteksi")
    
    if user.id in user_dict:
        chat_id = user.id
        user = user_dict[chat_id]
        
        keyboard = [[InlineKeyboardButton("Ya", callback_data=str(ONE)),
                     InlineKeyboardButton("Ubah Data", callback_data=str(TWO))]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
        # Send message with text and appended InlineKeyboard
        update.message.reply_text(
            "Halo {},\nBerikut adalah data Anda \
            \n\nUsia : {} \
            \nJenis kelamin : {} \
            \nNo AIMS : {} \
            \nCabang : {} \
            \n\nApakah mau menggunakan data yang sama atau tidak ?".format(user.nama, user.usia, user.gender, user.aims, user.cabang),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        # Tell ConversationHandler that we're in state `FIRST` now
        return THIRD
    else:
        update.message.reply_text("Silakan isi data diri terlebih dahulu.\n\nSiapa *nama* Anda ?", parse_mode=ParseMode.MARKDOWN)     
        return NAMA

def reinput_data(update, context):
    query = update.callback_query
    bot = context.bot
    
    bot.send_message(
        chat_id=query.message.chat_id,
        #message_id=query.message.message_id,
        text = "Silakan isi data diri terlebih dahulu.\n\nSiapa *nama* Anda ?",
        parse_mode=ParseMode.MARKDOWN
    )
    
    #update.message.reply_text("Silakan isi data diri terlebih dahulu.\n\nSiapa *nama* Anda ?", parse_mode=ParseMode.MARKDOWN)  
       
    return NAMA

def deteksi_over(update, context):
    # Get CallbackQuery from Update
    query = update.callback_query
    #user = query.message.chat
    
    chat_id = query.message.chat_id
    user = user_dict[chat_id]
    
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
    bot.send_message(
        chat_id=query.message.chat_id,
        #message_id=query.message.message_id,
        text = "Halo {},\nApakah dalam 3 hari terakhir Anda merasakan : \
        \n- gejala mirip masuk angin \
        \n- sakit tenggorokan ringan \
        \n- sedikit sakit (tidak demam, tidak lelah, masih makan dan minum secara normal) \
        \n\n*Tekan tombol dibawah ini :*".format(user.nama),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )
    return FIRST

# def reinput_nama(update, context):
#     query = update.callback_query
#     bot = context.bot
    
#     bot.send_message(
#         chat_id=query.message.chat_id,
#         #message_id=query.message.message_id,
#         text = "Nama yang anda ketikkan salah. Mohon input ulang lagi.\n\nSiapa *nama* Anda ?",
#         parse_mode=ParseMode.MARKDOWN
#     )
    
#     return GENDER

def check_alphabet_with_space(str_input):
    for w in str_input.split(' '):
        if not w.isalpha():
            return False
    return True
            
def nama(update, context):
    nama_user = update.message.text
    
    if check_alphabet_with_space(nama_user): #not nama_user.isalpha():
        chat_id = update.message.chat.id
        user = User(nama_user)
        user_dict[chat_id] = user
        
        reply_keyboard = [['Laki-laki', 'Perempuan']]
        
        update.message.reply_text("Apakah anda Laki-laki atau Perempuan?", reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))  

        return GENDER
    else:
        update.message.reply_text("Nama harus semuanya huruf. Mohon input ulang lagi.\n\nSiapa *nama* Anda ?", parse_mode=ParseMode.MARKDOWN)
        return NAMA
    

def gender(update, context):
    gender_user = update.message.text
    
    chat_id = update.message.chat.id
    user = user_dict[chat_id]
    user.gender = gender_user
    
    update.message.reply_text("Berapa *usia* Anda (tahun) ?", reply_markup = ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)  
    
    return USIA

def usia(update, context):
    usia_user = update.message.text
    
    if '/' in usia_user:
        update.message.reply_text("Usia yang anda ketikkan salah. Mohon input ulang lagi.\n\nBerapa *usia* Anda (tahun) ?", parse_mode=ParseMode.MARKDOWN)
        return USIA
    elif not usia_user.isnumeric():
        update.message.reply_text("Usia harus semuanya angka (dalam tahun). Mohon input ulang lagi.\n\nBerapa *usia* Anda (tahun) ?", parse_mode=ParseMode.MARKDOWN)
        return USIA
    elif len(usia_user) > 2:
        update.message.reply_text("Tidak mungkin!! Anda terlalu tua. Mohon input ulang lagi.\n\nBerapa *usia* Anda (tahun) ?", parse_mode=ParseMode.MARKDOWN)
        return USIA
    elif usia_user == '0':
        update.message.reply_text("Tidak mungkin!! Anda terlalu muda. Mohon input ulang lagi.\n\nBerapa *usia* Anda (tahun) ?", parse_mode=ParseMode.MARKDOWN)
        return USIA
    
    chat_id = update.message.chat.id
    user = user_dict[chat_id]
    user.usia = usia_user
    
    update.message.reply_text("Berapa *nomor AIMS* Anda ?", parse_mode=ParseMode.MARKDOWN)  
    
    return AIMS

def aims(update, context):
    aims_user = update.message.text
    
    if '/' in aims_user:
        update.message.reply_text("Nomor AIMS yang anda ketikkan salah. Mohon input ulang lagi.\n\nBerapa *nomor AIMS* Anda ?", parse_mode=ParseMode.MARKDOWN)
        return AIMS
    elif not aims_user.isnumeric():
        update.message.reply_text("Nomor AIMS harus semuanya angka. Mohon input ulang lagi.\n\nBerapa *nomor AIMS* Anda ?", parse_mode=ParseMode.MARKDOWN)
        return AIMS
    elif len(aims_user) != 5:
        update.message.reply_text("Nomor AIMS harus 5 angka. Mohon input ulang lagi.\n\nBerapa *nomor AIMS* Anda ?", parse_mode=ParseMode.MARKDOWN)
        return AIMS
    
    chat_id = update.message.chat.id
    user = user_dict[chat_id]
    user.aims = aims_user
    
    update.message.reply_text("Dari mana asal *Cabang* Anda ?", parse_mode=ParseMode.MARKDOWN)  
    
    return CABANG

def cabang(update, context):
    cabang_user = update.message.text
    
    #if re.match(r"([A-Za-z])+( [A-Za-z]+)", cabang_user) or cabang_user.isalpha(): #not nama_user.isalpha():
    if check_alphabet_with_space(cabang_user):
        chat_id = update.message.chat.id
        user = user_dict[chat_id]
        user.cabang = cabang_user
        
        user_tele = update.message.from_user
        logger.info("Captured data : %s %s %s %s %s %s %s %s", user_tele.id, user_tele.username, user_tele.first_name, user.nama, user.gender, user.usia, user.aims, user.cabang)
        

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
            \n\n*Tekan tombol dibawah ini :*".format(user.nama),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
        # Tell ConversationHandler that we're in state `FIRST` now
        return FIRST
    elif not cabang_user.isalpha():
        update.message.reply_text("Cabang harus semuanya huruf. Mohon input ulang lagi.\n\nDari mana asal *Cabang* Anda ?", parse_mode=ParseMode.MARKDOWN)
        return CABANG
    else:
        update.message.reply_text("Cabang yang anda ketikkan salah. Mohon input ulang lagi.\n\nDari mana asal *Cabang* Anda ?", parse_mode=ParseMode.MARKDOWN)
        return CABANG
        
    


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
    
    # bot.send_message(
    #     chat_id=query.message.chat_id,
    #     text =  "Pada hari ke 4, apakah Anda merasakan : \
    #             \n- sakit tenggorokan sedikit \
    #             \n- suara mulai serak \
    #             \n- suhu tubuh berkisar 36,5 C (kondisi ini tergantung orang) \
    #             \n- sakit kepala ringan \
    #             \n- diare ringan \
    #             \n\n*Tekan tombol dibawah ini :*",
    #     reply_markup=reply_markup,
    #     parse_mode=ParseMode.MARKDOWN
    # )
      
    bot.send_message(
        chat_id=query.message.chat_id,
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
    bot.send_message(
        chat_id=query.message.chat_id,
        text= "Sedang atau pernah mengalami :\n1. demam (>38 C)\n2. pilek\n3. batuk\n4. sesak napas",
        reply_markup=reply_markup
    )
    return FIRST

def three(update, context):
    """Show new choice of buttons"""

    query = update.callback_query
    
    user_tele = query.message.chat
    
    chat_id = user_tele.id
    user = user_dict[chat_id]
    db_write_diagnosis(user_tele, user, "sakit")
    
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=query.message.chat_id,
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
    bot.send_message(
        chat_id=query.message.chat_id,
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
    
    user_tele = query.message.chat
    
    chat_id = user_tele.id
    user = user_dict[chat_id]
    db_write_diagnosis(user_tele, user, "sehat")
    
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=query.message.chat_id,
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
    
    user_tele = query.message.chat
    
    chat_id = user_tele.id
    user = user_dict[chat_id]
    db_write_diagnosis(user_tele, user, "karantina")
    
    bot = context.bot
    keyboard = [
        [InlineKeyboardButton("Coba cek lagi", callback_data=str(ONE)),
         InlineKeyboardButton("Sudah cukup", callback_data=str(TWO))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(
        chat_id=query.message.chat_id,
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
              \n\n*Anda perlu pemeriksaan lanjutan ke RS rujukan COVID-19 atau ulangi pemeriksaan untuk bantuan konsultasi dengan relawan dokter kami*",
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
    bot.send_message(
        chat_id=query.message.chat_id,
        text="Semoga {} dan keluarga selalu sehat dan terlindung dari wabah COVID-19. Aamiin\n\nSilakan untuk mengakses menu lainnya:\n/info - Kabar terkini COVID-19 di Indonesia dan Dunia\n/cegah - Mencegah COVID-19".format(user_name)
    )
    
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def info(update, context):
    
    user = update.message.from_user
    db_write(user, "info")

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
    user = update.message.from_user
    db_write(user, "cegah")
    
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
            NAMA: [MessageHandler(Filters.text, nama)],
                   
            GENDER: [MessageHandler(Filters.text, gender)],
            
            USIA: [MessageHandler(Filters.text, usia)],
            
            AIMS: [MessageHandler(Filters.text, aims)],
            
            CABANG: [MessageHandler(Filters.text, cabang)],
            
            FIRST: [CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                    CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
                    CallbackQueryHandler(three, pattern='^' + str(THREE) + '$'),
                    CallbackQueryHandler(four, pattern='^' + str(FOUR) + '$'),
                    CallbackQueryHandler(five, pattern='^' + str(FIVE) + '$'),
                    CallbackQueryHandler(six, pattern='^' + str(SIX) + '$')],
            
            SECOND: [CallbackQueryHandler(deteksi_over, pattern='^' + str(ONE) + '$'),  
                     CallbackQueryHandler(end, pattern='^' + str(TWO) + '$')],
            
            THIRD: [CallbackQueryHandler(deteksi_over, pattern='^' + str(ONE) + '$'),  
                     CallbackQueryHandler(reinput_data, pattern='^' + str(TWO) + '$')]
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
    db_load()
    
    main()