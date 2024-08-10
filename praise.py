import telebot
from telebot import types
import uuid
# from config import *
import requests
from sqlalchemy import URL, create_engine
from sqlalchemy import Column, Integer, String, DateTime, Text,Boolean
from sqlalchemy.dialects.postgresql import JSONB, insert

from sqlalchemy import ARRAY
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import flask
from flask import request
from flask import render_template

import qrcode

from config import *


connection_string = URL.create(
  'postgresql',
  username = DB_USERNAME,
  password = DB_PASSWORD,
  host = DB_HOST,
  database = DB_DATABASE,
)

engine = create_engine(connection_string,pool_pre_ping=True)


print(engine)

Base = declarative_base()

class Teens(Base):
    
    __tablename__ = 'Teens Praise Data'
    user_id = Column(String(),unique=True,primary_key=True)
    paid = Column(Boolean(),unique=False,default=False,nullable=False)
    
    references = Column(String(), default='')
    payment_url =Column(String(),unique=False,default='a')
    tickets_bought =Column(String(),default='empty')

Base.metadata.create_all(engine)

def generate_payment(amount,user,type):

    user = user
    auth = f"Bearer {SECRET_KEY}"
    url = "https://api.paystack.co/transaction/initialize/"
    
    body = {'email':'soduro911@gmail.com'
            ,'amount':str(amount*100),
            "subaccount": "ACCT_lt51n1zmnr671bp",
             "transaction_charge": 650 ,
            'callback_url':str(CALLBACK_URL)
            }
    # ticket = uuid.uuid4()
    # print('Ticket generated:',ticket,'\n\n')
    
    response = requests.post(url,data=body,headers={'Authorization':auth,'content_type':'application/json'},)
    response = response.json()
    print(response)
    reference = response['data']['reference']
    pay_url = response['data']['authorization_url']
    
    with engine.connect() as conn:
        session = sessionmaker(bind=engine)
        session = session()
        # teen = session.query(Teens).all()
        user_with_ref = session.query(Teens).filter_by(user_id=str(user)).one_or_none()
        
        if user_with_ref is None:

            new_user = Teens(user_id=str(user),payment_url=reference,references=reference)
            new_user.tickets_bought = str(int(1))
            session.add(new_user)
            session.commit()
            print('New user tickets updated')
        
        if user_with_ref:

            references = str(user_with_ref.references)
             
            print(references)
            references = references+' ' + reference
            print(references)
            user_with_ref.references = references

            session.commit()

            if user_with_ref.tickets_bought == 'empty':
                user_with_ref.tickets_bought = str(int(1))
                print('User already bought, tk num updated')
                session.commit()
            else:
                user_with_ref.tickets_bought = str(int(user_with_ref.tickets_bought) + 1)
                print('tk num updatedd')
                session.commit()    


        return {'url':pay_url,'reference':reference}

app = flask.Flask(__name__)

def send_ticket(pay_ref,ticket_num):
    connection_string = URL.create(
  'postgresql',
  username = DB_USERNAME,
  password = DB_PASSWORD,
  host = DB_HOST,
  database = DB_DATABASE,
)
    message = f'Payment received, your ticket number is {ticket_num}'
    engine = create_engine(connection_string,pool_pre_ping=True)
    session = sessionmaker(bind=engine)
    session = session()
    teens_data = session.query(Teens).all()
    
    for teen in teens_data:
        
        references = teen.references.split()  # Split references by space
        user_id = teen.user_id
        print(f"User ID: {user_id}")
        print(f"References: {references}")
        print("-----")

        for reference_all in references:
            if reference_all == pay_ref:
                index = references.index(reference_all)
                print(index)
                print('User with ticket found')
                print(user_id)
                qr = qrcode.QRCode(
                            version=2,
                            error_correction=qrcode.constants.ERROR_CORRECT_L,
                            box_size=10,
                            border=1,
                        )
                qr.add_data(VERIFY_ENDPOINT+'verify?ticket_num='+ticket_num)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                img.save('ticket.png')
                bot.send_message(chat_id=user_id,text=message,parse_mode='HTML')
                print(references)
                print('this ref ',references)
                references.remove(pay_ref)
                teen.references = " ".join(references)
                
                print('nw',references)
                print(teen.references)
                session.commit()                
                bot.send_photo(chat_id=user_id,photo=open('ticket.png','rb'))


    
@app.route('/',methods=['GET','POST'])
def alive():
    print('request made,ress')
    return 'Im alive'

@app.route('/genv',methods=['GET'])


def ticket_gen():

    trxref = request.args.get('trxref')
    reference = request.args.get('reference')
    print(trxref,'\n\n',reference)
    print(trxref==reference)
    # wrequest = request
    connection_string = URL.create(
    'postgresql',
    username = PGUSER,
    password = PGPASSWORD,
    host = PGHOST,
    database = PGDATABASE,
    )

    Tengine = create_engine(connection_string,pool_pre_ping=True)


    print(Tengine)

    TBase = declarative_base()

    class Teens_Tickets(TBase):
        
        __tablename__ = 'Teens Praise Tickets'
        ticket_num = Column(String(),default='',unique=True,primary_key=True)
        ticket_qr = Column(String(),default='')
        ticket_type = Column(String(),default='')

    TBase.metadata.create_all(Tengine)

    auth = f"Bearer {SECRET_KEY}"
    reference = reference
    url=f"https://api.paystack.co/transaction/verify/{reference}"
    print(url)
            
    response = requests.get(url,headers={'Authorization':auth,'content_type':'application/json'})
    response = response.json()
    print(response)
            
    if response['status'] and response['data']['status'] == 'success' and response['data']['reference'] == reference and response['data']['amount']==int(STANDARD*100):
        
        standard_ticket = uuid.uuid4()
        print('This tick',standard_ticket)
        standard_ticket = str(standard_ticket)+'standard'
        print('Standard ticket has been generated')



        with engine.connect() as conn:
            session = sessionmaker(bind=Tengine)
            session = session()
            # teen = session.query(Teens).all()
            ticket = session.query(Teens_Tickets).filter_by(ticket_num=str(standard_ticket)).one_or_none()
        
            if ticket is None:
                ticket = Teens_Tickets(ticket_num=standard_ticket)
                session.add(ticket)
                session.commit()
                send_ticket(pay_ref=reference,ticket_num=standard_ticket)                
                print('Added to db tickets sucss')
                return render_template('success.html')

    if response['status'] and response['data']['status'] == 'success' and response['data']['reference'] == reference and response['data']['amount']==int(DOUBLE*100):
        double_ticket = uuid.uuid4()
        print('This tick',double_ticket)
        double_ticket = str(double_ticket)+'double'
        print('Double ticket has been generated')

        with engine.connect() as conn:
            session = sessionmaker(bind=Tengine)
            session = session()
            # teen = session.query(Teens).all()
            ticket = session.query(Teens_Tickets).filter_by(ticket_num=str(double_ticket)).one_or_none()
        
            if ticket is None:
                ticket = Teens_Tickets(ticket_num=double_ticket)
                session.add(ticket)
                session.commit()
                send_ticket(pay_ref=reference,ticket_num=double_ticket)                
                print('Added to db tickets sucss')
                return render_template('success.html')

    if response['status'] and response['data']['status'] == 'success' and response['data']['reference'] == reference and response['data']['amount']==int(VIP*100):
        vip_ticket = uuid.uuid4()
        print('This tick',vip_ticket)
        vip_ticket = str(vip_ticket)+'vip'
        print('Vip ticket has been generated')

        with engine.connect() as conn:
            session = sessionmaker(bind=Tengine)
            session = session()
            # teen = session.query(Teens).all()
            ticket = session.query(Teens_Tickets).filter_by(ticket_num=str(vip_ticket)).one_or_none()
        
            if ticket is None:
                ticket = Teens_Tickets(ticket_num=vip_ticket)
                session.add(ticket)
                session.commit()
                send_ticket(pay_ref=reference,ticket_num=vip_ticket)                
                print('Added to db tickets sucss')
                return render_template('success.html')


@app.route('/verify',methods=['GET'])
def validate_ticket():
    connection_string = URL.create(
    'postgresql',
    username = PGUSER,
    password = PGPASSWORD,
    host = PGHOST,
    database = PGDATABASE,
    )

    Tengine = create_engine(connection_string,pool_pre_ping=True)
    TBase = declarative_base()

    class Teens_Tickets(TBase):
        
        __tablename__ = 'Teens Praise Tickets'
        ticket_num = Column(String(),default='',unique=True,primary_key=True)
        ticket_qr = Column(String(),default='')
        ticket_type = Column(String(),default='')

    with engine.connect() as conn:
            session = sessionmaker(bind=Tengine)
            session = session()
            # teen = session.query(Teens).all()
            ticket = session.query(Teens_Tickets).filter_by(ticket_num=str(request.args.get('ticket_num'))).one_or_none()
            print(ticket)
            if ticket:
                return 'Ticket passed is valid'
            else:
                return 'Invalid ticket please check ticket details'

               
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):
   
   keyboard = types.InlineKeyboardMarkup(row_width=1)
   buy = types.InlineKeyboardButton("ꜱᴇᴄᴜʀᴇ ᴀ ᴛɪᴄᴋᴇᴛ",callback_data='buy')
   check = types.InlineKeyboardButton("ᴠᴀʟɪᴅᴀᴛᴇ ᴛɪᴄᴋᴇᴛ",callback_data='validate')
   
   keyboard.add(buy)
   keyboard.add(check)

   bot.send_message(message.chat.id,WELCOME,parse_mode='HTML',reply_markup=keyboard)

@bot.message_handler(func=lambda message:True)

def validate(message):
    if message.reply_to_message:
        
        print('user replied to to msg')
        print(message.text)
        
        replied_t=message.reply_to_message.text
        print('Here to')
        check = 'Please send your ticket number to validate ticket'
        
        if replied_t == check:
            print('Passsed')
            connection_string = URL.create(
            'postgresql',
            username = PGUSER,
            password = PGPASSWORD,
            host = PGHOST,
            database = PGDATABASE,
            )

            Tengine = create_engine(connection_string,pool_pre_ping=True)
            TBase = declarative_base()

            class Teens_Tickets(TBase):
                
                __tablename__ = 'Teens Praise Tickets'
                ticket_num = Column(String(),default='',unique=True,primary_key=True)
                ticket_qr = Column(String(),default='')
                ticket_type = Column(String(),default='')

            with engine.connect() as conn:
                session = sessionmaker(bind=Tengine)
                session = session()
                # teen = session.query(Teens).all()
                ticket = session.query(Teens_Tickets).filter_by(ticket_num=str(message.text)).one_or_none()
        
                if ticket is None:
                    reply = 'Ticket sent is invalid. Please correct details\n\n'
                    keyboard = types.InlineKeyboardMarkup()
                    continue_b = types.InlineKeyboardButton('Continue',callback_data='continue-nue')
                    keyboard.add(continue_b) 
                    bot.send_message(message.from_user.id,text=reply,reply_markup=keyboard)
                if ticket:
                    reply = 'Ticket is valid\n\n'
                    keyboard = types.InlineKeyboardMarkup()
                    continue_b = types.InlineKeyboardButton('Continue',callback_data='continue-nue')
                    keyboard.add(continue_b) 
                    bot.send_message(message.from_user.id,text=reply,reply_markup=keyboard)

@bot.message_handler(func=lambda x:True)
def messages(message):
    print(message)

    if message.text == 'Cancel🚫':
        keyboard = types.InlineKeyboardMarkup()
        purchase_ticket = types.InlineKeyboardButton('RETRY',callback_data='retry')
        keyboard.add(purchase_ticket)
        bot.send_message(message.chat.id,RETRY,parse_mode='HTML',reply_markup=keyboard)

    if message.text == 'RETRY':
        pass

@bot.callback_query_handler(func=lambda message:True)
def pay(message):
    print(message)
    if message.data =='buy':
        
        keyboard = types.InlineKeyboardMarkup()
        cancel = types.InlineKeyboardButton('Cancel🚫',callback_data='Cancel🚫')
        standard = types.InlineKeyboardButton('Standard (50)',callback_data='standard')
        double =  types.InlineKeyboardButton('Double (80)',callback_data='double')
        vip =  types.InlineKeyboardButton('Vip (120)',callback_data='vip')
        
        keyboard.add(standard)
        keyboard.add(double)
        keyboard.add(vip)
        keyboard.add(cancel)

        bot.send_message(message.from_user.id,text=CHOICE,reply_markup=keyboard)
    
    if message.data =='Cancel🚫':        
        keyboard = types.InlineKeyboardMarkup()
        purchase_ticket = types.InlineKeyboardButton('RETRY',callback_data='retry')
        keyboard.add(purchase_ticket)
        bot.send_message(message.from_user.id,RETRY,parse_mode='HTML',reply_markup=keyboard)

    if message.data == 'retry':
        keyboard = types.InlineKeyboardMarkup()
        cancel = types.InlineKeyboardButton('Cancel🚫',callback_data='Cancel🚫')
        standard = types.InlineKeyboardButton('Standard GHC 50)',callback_data='standard')
        double =  types.InlineKeyboardButton('Double GHC 80',callback_data='double')
        vip =  types.InlineKeyboardButton('Vip GHC 120',callback_data='vip')
        
        keyboard.add(standard)
        keyboard.add(double)
        keyboard.add(vip)
        keyboard.add(cancel)
        bot.send_message(message.from_user.id,text=CHOICE,reply_markup=keyboard)        
    
    if message.data == 'standard':
        
        pay_url = generate_payment(STANDARD,message.from_user.id,'standard')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        pay = types.InlineKeyboardButton('Complete Payment',url=pay_url['url'])
        pay_status = types.InlineKeyboardButton('Check Status',callback_data='status')
        cancel = types.InlineKeyboardButton('Cancel🚫',callback_data='Cancel🚫')
        
        keyboard.add(pay,pay_status)
        keyboard.add(cancel)
        
        bot.send_message(message.from_user.id,text=PAY,reply_markup=keyboard)

    if message.data == 'double':
        
        pay_url = generate_payment(DOUBLE,message.from_user.id,'double')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        pay = types.InlineKeyboardButton('Complete Payment',url=pay_url['url'])
        pay_status = types.InlineKeyboardButton('Check Status',callback_data='status')
        cancel = types.InlineKeyboardButton('Cancel🚫',callback_data='Cancel🚫')
        
        keyboard.add(pay,pay_status)
        keyboard.add(cancel)
        
        bot.send_message(message.from_user.id,text=PAY,reply_markup=keyboard)

    if message.data == 'vip':
        
        pay_url = generate_payment(VIP,message.from_user.id,'vip')
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        pay = types.InlineKeyboardButton('Complete Payment',url=pay_url['url'])
        pay_status = types.InlineKeyboardButton('Check Status',callback_data='status')
        cancel = types.InlineKeyboardButton('Cancel🚫',callback_data='Cancel🚫')
        
        keyboard.add(pay,pay_status)
        keyboard.add(cancel)
        
        bot.send_message(message.from_user.id,text=PAY,reply_markup=keyboard)

  
    if message.data == 'validate':
        print('vallllll')
        rep_message = '''
Please send your ticket number to validate ticket        
        
        '''
        keyboard = types.ForceReply()
        bot.send_message(message.from_user.id,text=rep_message,reply_markup=keyboard)
      
    if message.data == 'continue-nue':
        keyboard = types.InlineKeyboardMarkup()
        cancel = types.InlineKeyboardButton('Cancel🚫',callback_data='Cancel🚫')
        standard = types.InlineKeyboardButton('Standard (50)',callback_data='standard')
        double =  types.InlineKeyboardButton('Double (80)',callback_data='double')
        vip =  types.InlineKeyboardButton('Vip (120)',callback_data='vip')
        
        keyboard.add(standard)
        keyboard.add(double)
        keyboard.add(vip)
        keyboard.add(cancel)

        bot.send_message(message.from_user.id,text=CHOICE,reply_markup=keyboard)        

import threading
import time
def run_fl():
    #  app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port=5000, debug=False)

def run_bot():
    bot.polling(non_stop=True, interval=2)
  
poll = threading.Thread(target=run_bot)
serv = threading.Thread(target=run_fl)



servers = [poll, serv]
for s in servers:
    s.start()

#
