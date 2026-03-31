import telebot
import random
import string
from datetime import datetime, timedelta
import traceback

# ================== CONFIG ==================
TOKEN = "8626801064:AAGmujo1y1YX4Cnb1EdJ_yU7RbKR0Eaqcm4"
ADMIN_IDS = [7499054129, 5734158631]
FAKE_USERS_COUNT = 129360  # количество фейковых пользователей

bot = telebot.TeleBot(TOKEN)
users = {}
checks = {}
invoices = {}

# ================== USER ==================
def register_user(user_id, username=None, first_name=None):
    if user_id not in users:
        if user_id in ADMIN_IDS:
            users[user_id] = {
                'btc': 999999,
                'eth': 999999,
                'usdt': 999999,
                'ton': 999999,
                'bnb': 999999,
                'stars': 999999,
                'rub': 9999999,
                'uan': 9999999,
                'kzt': 9999999,
                'is_admin': True,
                'username': username,
                'first_name': first_name,
                'last_action': None
            }
        else:
            users[user_id] = {
                'btc': 0,
                'eth': 0,
                'usdt': 0,
                'ton': 0,
                'bnb': 0,
                'stars': 0,
                'rub': 0,
                'uan': 0,
                'kzt': 0,
                'is_admin': False,
                'username': username,
                'first_name': first_name,
                'last_action': None
            }
    elif 'last_action' not in users[user_id]:
        users[user_id]['last_action'] = None

# ================== KEYBOARDS ==================
def get_main_keyboard(user_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        telebot.types.InlineKeyboardButton("👛 Кошелёк", callback_data="wallet"),
        telebot.types.InlineKeyboardButton("🔄 Обмен", callback_data="exchange")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("📤 Отправить", callback_data="send_menu"),
        telebot.types.InlineKeyboardButton("📥 Получить", callback_data="receive")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("🎫 Чеки", callback_data="checks_menu"),
        telebot.types.InlineKeyboardButton("📊 Счета", callback_data="invoices_menu")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("💱 P2P", callback_data="p2p"),
        telebot.types.InlineKeyboardButton("📈 Биржа", callback_data="exchange_rates")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("🎁 Розыгрыши", callback_data="giveaways"),
        telebot.types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
    )
    markup.row(telebot.types.InlineKeyboardButton("💸 Вывод", callback_data="withdraw_menu"))
    if user_id in ADMIN_IDS:
        markup.row(telebot.types.InlineKeyboardButton("👑 Админ панель", callback_data="admin_panel"))
    return markup

def edit_menu(call, text, buttons):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    for row in buttons:
        markup.row(*[telebot.types.InlineKeyboardButton(t, callback_data=d) for t, d in row])
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
    except telebot.apihelper.ApiTelegramException:
        try:
            bot.send_message(call.from_user.id, text, reply_markup=markup)
        except:
            pass

# ================== START ==================
@bot.message_handler(commands=['start'])
def start(message):
    register_user(message.from_user.id, message.from_user.username, message.from_user.first_name)

    total_users = FAKE_USERS_COUNT + len(users)

    bot.send_message(
        message.chat.id,
        f"👥 {total_users:,} пользователей в боте\n\n"
        "🪙 Antarctic Wallet📥\n\n"
        "Покупайте, продавайте, храните, отправляйте и платите криптовалютой.\n\n"
        "Весенний фестиваль с Antarctic Wallet🎁",
        reply_markup=get_main_keyboard(message.from_user.id)
    )

# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        user_id = call.from_user.id
        register_user(user_id)
        try:
            bot.answer_callback_query(call.id)
        except:
            pass

        # ---------- Главное меню ----------
        if call.data == "wallet":
            total_users = FAKE_USERS_COUNT + len(users)
            text = f"👥 {total_users:,} пользователей в боте\n\n👛 Кошелёк\n\n"
            total_usd = 0
            rates = {
                'btc':65000,'eth':3500,'usdt':1,'ton':5.5,'bnb':400,
                'stars':0.1,'rub':0.013,'uan':0.15,'kzt':0.0022
            }
            emojis = {
                'btc':'₿','eth':'Ξ','usdt':'💵','ton':'💎','bnb':'🪙',
                'stars':'🌟','rub':'₽','uan':'¥','kzt':'₸'
            }
            for curr in ['btc','eth','usdt','ton','bnb','stars','rub','uan','kzt']:
                amount = users[user_id][curr]
                usd = amount*rates[curr]
                total_usd += usd
                text += f"{emojis[curr]} {curr.upper()}: {amount:.8f}\n   ${usd:,.2f}\n\n"
            text += f"💰 Общий баланс: ${total_usd:,.2f}"
            edit_menu(call,text,[[("📥 Получить","receive"),("📤 Отправить","send_menu")],[("◀️ Назад","back")]])

        elif call.data == "send_menu":
            users[user_id]['last_action'] = None
            text = "📤 Отправить\nВыберите способ:"
            buttons = [
                [("Пользователю","send_user"),("Чеком","send_check")],
                [("Счетом","send_invoice"),("На адрес","send_address")],
                [("◀️ Назад","back")]
            ]
            edit_menu(call,text,buttons)

        elif call.data == "send_user":
            users[user_id]['last_action'] = 'send_user'
            bot.send_message(user_id,"Введите в чат: @username сумма валюта")

        elif call.data == "send_check":
            users[user_id]['last_action'] = 'send_check'
            bot.send_message(user_id,"Введите сумму и валюту для чека, например: 0.01 BTC")

        elif call.data == "send_invoice":
            users[user_id]['last_action'] = 'send_invoice'
            bot.send_message(user_id,"Введите сумму и валюту для счета, например: 100 USDT")

        elif call.data == "send_address":
            users[user_id]['last_action'] = 'send_address'
            bot.send_message(user_id,"Введите адрес и сумму, например:\nBTC 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa 0.01")

        # ---------- Чеки ----------
        elif call.data == "checks_menu":
            text = "🎫 Чеки\nСоздавайте и активируйте чеки"
            buttons = [[("Создать чек","create_check_menu"),("Активировать","activate_check_menu")],[("◀️ Назад","back")]]
            edit_menu(call,text,buttons)

        elif call.data == "create_check_menu":
            users[user_id]['last_action'] = 'create_check'
            buttons = [
                [("₿ BTC","check_curr_BTC"),("Ξ ETH","check_curr_ETH")],
                [("💵 USDT","check_curr_USDT"),("💎 TON","check_curr_TON")],
                [("🌟 STARS","check_curr_STARS"),("₽ RUB","check_curr_RUB")],
                [("¥ UAN","check_curr_UAN"),("₸ KZT","check_curr_KZT")],
                [("◀️ Назад","back")]
            ]
            edit_menu(call,"🎫 Создание чека\nВыберите валюту:",buttons)

        elif call.data.startswith("check_curr_"):
            currency = call.data.replace("check_curr_","")
            users[user_id]['last_action'] = f'create_check_{currency}'
            bot.send_message(user_id,f"Введите сумму для чека ({currency}):")

        elif call.data == "activate_check_menu":
            users[user_id]['last_action'] = 'activate_check'
            bot.send_message(user_id,"Введите код чека в чат:")

        # ---------- Вывод средств ----------
        elif call.data == "withdraw_menu":
            users[user_id]['last_action'] = 'withdraw_choose_currency'
            buttons = [
                [("₿ BTC","withdraw_BTC"),("Ξ ETH","withdraw_ETH")],
                [("💵 USDT","withdraw_USDT"),("💎 TON","withdraw_TON")],
                [("🪙 BNB","withdraw_BNB"),("🌟 STARS","withdraw_STARS")],
                [("₽ RUB","withdraw_RUB"),("₸ KZT","withdraw_KZT")],
                [("◀️ Назад","back")]
            ]
            edit_menu(call,"💸 Вывод средств\nВыберите валюту:", buttons)

        elif call.data.startswith("withdraw_"):
            currency = call.data.replace("withdraw_","").lower()
            users[user_id]['last_action'] = f'withdraw_amount_{currency}'
            bot.send_message(user_id,f"Введите сумму для вывода {currency.upper()}:")

        # ---------- Остальные меню ----------
        elif call.data == "exchange":
            text = "🔄 Обмен\nВыберите пару:"
            buttons = [
                [("BTC→USDT","ex_btc_usdt"),("USDT→BTC","ex_usdt_btc")],
                [("ETH→USDT","ex_eth_usdt"),("USDT→ETH","ex_usdt_eth")],
                [("TON→USDT","ex_ton_usdt"),("USDT→TON","ex_usdt_ton")],
                [("◀️ Назад","back")]
            ]
            edit_menu(call,text,buttons)

        elif call.data == "receive":
            text = "📥 Получить\nВаши адреса:\n₿ BTC: ...\nΞ ETH: ...\n💵 USDT: ...\n💎 TON: ..."
            edit_menu(call,text,[[("◀️ Назад","back")]])

        elif call.data == "p2p":
            text = "💱 P2P Торговля\nUSDT: 95.5 RUB\nBTC: 6,150,000 RUB\nETH: 332,000 RUB"
            edit_menu(call,text,[[("Купить","p2p_buy"),("Продать","p2p_sell")],[("◀️ Назад","back")]])

        elif call.data == "exchange_rates":
            text = "📈 Биржа\nBTC/USDT: 65,000\nETH/USDT: 3,500\nBNB/USDT: 400\nTON/USDT: 5.50"
            edit_menu(call,text,[[("Обменять","exchange")],[("◀️ Назад","back")]])

        elif call.data == "giveaways":
            text = "🎁 Розыгрыши\nАктивных розыгрышей: 3"
            edit_menu(call,text,[[("Участвовать","giveaway_join")],[("◀️ Назад","back")]])

        elif call.data == "settings":
            text = "⚙️ Настройки\n🌐 Язык: Русский\n🔔 Уведомления: Вкл\n🔐 2FA: Выкл"
            buttons = [[("Язык","settings_lang"),("Уведомления","settings_notify")],[("Безопасность","settings_security"),("◀️ Назад","back")]]
            edit_menu(call,text,buttons)

        elif call.data == "invoices_menu":
            text = "📊 Счета\nСоздайте или просмотрите счета"
            buttons = [[("Создать счет","create_invoice")],[("◀️ Назад","back")]]
            edit_menu(call,text,buttons)

        elif call.data == "admin_panel" and user_id in ADMIN_IDS:
            active_checks = len([c for c in checks.values() if c.get('active')])
            active_invoices = len([i for i in invoices.values() if i['status']=='pending'])
            text = f"👑 АДМИН ПАНЕЛЬ\nПользователей: {len(users)}\nАктивных чеков: {active_checks}\nАктивных счетов: {active_invoices}"
            buttons = [[("Создать чек","create_check_admin"),("Мои чеки","my_checks")],[("◀️ Назад","back")]]
            edit_menu(call,text,buttons)

        elif call.data == "back":
            try:
                bot.edit_message_text("Главное меню:",user_id,call.message.message_id,reply_markup=get_main_keyboard(user_id))
            except:
                bot.send_message(user_id,"Главное меню:",reply_markup=get_main_keyboard(user_id))

    except Exception:
        print(traceback.format_exc())

# ================== TEXT HANDLER ==================
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text.strip()
    register_user(user_id)
    action = users[user_id].get('last_action')

    # ---------- Отправка пользователю ----------
    if action == 'send_user':
        parts = text.split()
        if len(parts) == 3:
            username = parts[0][1:].lower()
            try:
                amount = float(parts[1].replace(",","."))
                currency = parts[2].lower()
                recipient_id = None
                for uid, u in users.items():
                    if u.get('username') and u['username'].lower() == username:
                        recipient_id = uid
                        break
                if recipient_id is None:
                    bot.reply_to(message,"❌ Пользователь не найден")
                    return
                if users[user_id][currency] < amount:
                    bot.reply_to(message,"❌ Недостаточно средств")
                    return
                users[user_id][currency] -= amount
                users[recipient_id][currency] += amount
                bot.reply_to(message,f"✅ Успешно отправлено {amount} {currency.upper()} пользователю @{username}")
                bot.send_message(recipient_id,f"💰 Вам пришло {amount} {currency.upper()} от @{message.from_user.username}")
                users[user_id]['last_action'] = None
            except:
                bot.reply_to(message,"❌ Ошибка формата суммы или валюты")
        return

    # ---------- Создание чека ----------
    if action and action.startswith('create_check_'):
        try:
            amount = float(text.replace(",","."))
            currency = action.replace('create_check_','')
            if users[user_id][currency.lower()] < amount:
                bot.reply_to(message,"❌ Недостаточно средств")
                return
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            checks[code] = {
                'creator_id': user_id,
                'amount': amount,
                'currency': currency.upper(),
                'active': True,
                'expires_at': datetime.now()+timedelta(hours=24)
            }
            users[user_id][currency.lower()] -= amount
            bot.reply_to(message,f"✅ Чек создан!\nКод: {code}\n💰 {amount} {currency.upper()}\nСрок: 24 часа")
            users[user_id]['last_action'] = None
        except:
            bot.reply_to(message,"❌ Ошибка суммы")
        return

    # ---------- Активация чека ----------
    if action == 'activate_check':
        code = text.upper()
        if code in checks and checks[code]['active']:
            c = checks[code]
            if c['expires_at'] < datetime.now():
                c['active'] = False
                bot.reply_to(message,"❌ Срок действия чека истек")
                users[user_id]['last_action'] = None
                return
            users[user_id][c['currency'].lower()] += c['amount']
            c['active'] = False
            bot.reply_to(message,f"✅ Чек активирован!\n💰 Получено: {c['amount']} {c['currency']}")
            users[user_id]['last_action'] = None
            return
        else:
            bot.reply_to(message,"❌ Неверный код чека")
            return

    # =================== ВЫВОД ===================
    if action and action.startswith('withdraw_amount_'):
        currency = action.replace('withdraw_amount_','').lower()
        cleaned_text = ''.join(c for c in text if c.isdigit() or c in [',','.'])
        if not cleaned_text:
            bot.send_message(user_id, f"Введите сумму для вывода {currency.upper()}:")
            return
        try:
            amount = float(cleaned_text.replace(",","."))
            if amount <= 0:
                bot.send_message(user_id, f"❌ Сумма должна быть больше нуля. Введите сумму для вывода {currency.upper()}:")
                return
            if amount > users[user_id][currency]:
                bot.reply_to(message,"❌ Недостаточно средств")
                return
            users[user_id]['withdraw_amount'] = amount
            if currency.upper() == "STARS":
                users[user_id]['last_action'] = f'withdraw_username_{currency}'
                bot.send_message(user_id,"Введите ваш @username для вывода STARS:")
            elif currency.upper() in ["RUB","KZT"]:
                users[user_id]['last_action'] = f'withdraw_recipient_{currency}'
                bot.send_message(user_id,f"Введите номер карты или телефона для вывода {currency.upper()}:")
            else:
                users[user_id]['last_action'] = f'withdraw_address_{currency}'
                bot.send_message(user_id,f"Введите адрес для вывода {currency.upper()}:")
        except:
            bot.send_message(user_id,f"Введите сумму для вывода {currency.upper()}:")
        return

    if action and (action.startswith('withdraw_address_') or action.startswith('withdraw_username_') or action.startswith('withdraw_recipient_')):
        currency = action.split("_")[-1].lower()
        amount = users[user_id].get('withdraw_amount',0)
        if amount <= 0:
            bot.reply_to(message,"❌ Ошибка: сумма не указана")
            users[user_id]['last_action'] = None
            return
        fee = amount*0.03
        net = amount - fee
        if action.startswith('withdraw_username_'):
            username = text.strip()
            users[user_id][currency] -= amount
            bot.reply_to(message,
                f"✅ Вывод начался!\n"
                f"Валюта: {currency.upper()}\n"
                f"Сумма: {amount}\n"
                f"К зачислению: {net:.2f}\n"
                f"{username}\n"
                "Средства поступят в течение часа ⏱️"
            )
        elif action.startswith('withdraw_recipient_'):
            recipient = text.strip()
            users[user_id][currency] -= amount
            bot.reply_to(message,
                f"✅ Вывод начался!\n"
                f"Валюта: {currency.upper()}\n"
                f"Сумма: {amount}\n"
                f"Комиссия: 3% ({fee:.2f})\n"
                f"К зачислению: {net:.2f}\n"
                f"По номеру карты/по номеру телефона: {recipient}\n"
                "Средства поступят в течение часа ⏱️"
            )
        else:
            address = text.strip()
            users[user_id][currency] -= amount
            bot.reply_to(message,
                f"✅ Вывод начался!\n"
                f"Валюта: {currency.upper()}\n"
                f"Сумма: {amount}\n"
                f"Комиссия: 3% ({fee:.2f})\n"
                f"К зачислению: {net:.2f}\n"
                f"Адрес/номер: {address}\n"
                "Средства поступят в течение часа ⏱️"
            )
        users[user_id]['last_action'] = None
        users[user_id]['withdraw_amount'] = 0
        return

    bot.reply_to(message,"Используйте кнопки меню или введите корректный код/сумму.")

# ================== RUN BOT ==================
if __name__ == "__main__":
    print("CRYPTO BOT STARTED")
    bot.infinity_polling(none_stop=True, interval=0)