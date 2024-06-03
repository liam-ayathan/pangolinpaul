from telegram import (
    Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice, InlineKeyboardButton,
    InlineKeyboardMarkup, PhotoSize, InputFile
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    ConversationHandler, MessageHandler, StringCommandHandler,
    filters, PreCheckoutQueryHandler, CallbackQueryHandler, CallbackContext,
)
from dotenv import load_dotenv
import logging
import io
import os
from PIL import Image
from keep_alive import keep_alive
keep_alive()

load_dotenv() #important!

# Loggerdea
logger = logging.getLogger(__name__)

# Telegram
TELE_TOKEN = os.getenv("TELE_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

PORT = int(os.environ.get('PORT', 5000))
ROUTE, GET_API_ID, GET_API_HASH_TRIGGER_HP, COMPLETE_PROFILE, ADD_CODE = range(5) # defining different states

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    
    # code below deletes users message to the bot
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    try:
        if context.user_data['unknown_message'] != None:
            unknown_message = context.user_data['unknown_message']
            await unknown_message.delete()
    except Exception as e:
        print("unknown message is not set")

    try:
        if context.user_data['original_message'] != None:
            original_message = context.user_data['original_message']
            await original_message.delete()
    except Exception as e:
        print("original message is not set")

    try:
        if context.user_data['animal_message'] != None:
            animal_message = context.user_data['animal_message']
            await animal_message.delete()
    except Exception as e:
        print("animal message is not set")

    keyboard = [
        [InlineKeyboardButton("Otter 🦦", callback_data="view_otter"),],
        [InlineKeyboardButton("Wild Boar 🐗", callback_data="view_boar"),],
        [InlineKeyboardButton("Snake 🐍", callback_data="view_snake"),],
        [InlineKeyboardButton("Monkey 🐒", callback_data="view_monkey"),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = ("Hey there! 🎉\n\n"
               "Please select one of the options below so that we can alert the right person to help you!\n\n")
    
    original_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            reply_markup=reply_markup
        )
    
    context.user_data['original_message'] = original_message
    # target_user_id = GROUP_ID  # Replace with the actual target user ID (important thoughts)
    # print(update.effective_chat.id)
    # await context.bot.send_message(
    #     chat_id=target_user_id,
    #     text="Hello again my friend"
    # )
    return ROUTE

async def view_otter(update, context: ContextTypes.DEFAULT_TYPE):

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    # desired_width = 300  
    # desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(f'./images/otter.jpg', 'rb') as f:
        image = Image.open(f)
        # resized_image = image.resize((desired_width, desired_height))

        bio = io.BytesIO()
        # resized_image.save(bio, format='JPEG')
        image.save(bio,format='JPEG')
        bio.seek(0)

    # User Chat
    message = ("Otters may be playful, but they need their space. Do not approach too closely or attempt to touch them! \n\n"
               "If you spot an otter, remain calm and avoid sudden movements or loud noises. Otters are curious but can be easily scared away. \n\n"
               "We have reached out to the relevant experts, sit tight, help is on the way 👍\n\n")
    
    animal_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename='otter.jpg'),
                                                   caption=message,
                                                   reply_markup=reply_markup)

    context.user_data['animal_message'] = animal_message

    # Reset bio for the next use
    # Image Handling: The image is loaded and saved into an in-memory bio buffer, which is then used to send the image. The bio.seek(0) resets the buffer to the beginning, allowing it to be reused for the helper chat.
    bio.seek(0)

    # Helper chat
    try:
        user_handle = update.effective_user.username #assuming someone has a handle some people don't
        message = ("🚨 Someone has just spotted an Otter! 🚨\n\n"
                  f"@liamayathan please reach out to @{user_handle} to provide assistance 👍\n\n")
        
        help_message = await context.bot.send_photo(chat_id=GROUP_ID,
                                                      photo=InputFile(bio, filename='otter.jpg'),
                                                      caption=message)
        
    except Exception as e:
        print("The exception is", e)
    
    return ROUTE

async def view_boar(update, context: ContextTypes.DEFAULT_TYPE):

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    # desired_width = 300  
    # desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(f'./images/boar.jpg', 'rb') as f:
        image = Image.open(f)
        # resized_image = image.resize((desired_width, desired_height))

        bio = io.BytesIO()
        # resized_image.save(bio, format='JPEG')
        image.save(bio,format='JPEG')
        bio.seek(0)

    # User Chat
    message = ("If you spot a wild boar, remain calm and avoid sudden movements. Slowly back away from the animal! \n\n"
               "If you see adult wild boars with young piglets, exercise extra caution. These adults may become defensive if they perceive a threat to their offspring. \n\n"
               "We have reached out to the relevant experts, sit tight, help is on the way 👍\n\n")
    
    animal_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename='boar.jpg'),
                                                   caption=message,
                                                   reply_markup=reply_markup)

    context.user_data['animal_message'] = animal_message

    # Reset bio for the next use
    # Image Handling: The image is loaded and saved into an in-memory bio buffer, which is then used to send the image. The bio.seek(0) resets the buffer to the beginning, allowing it to be reused for the helper chat.
    bio.seek(0)

    # Helper chat
    try:
        user_handle = update.effective_user.username #assuming someone has a handle some people don't
        message = ("🚨 Someone has just spotted a Wild Boar! 🚨\n\n"
                  f"@valelerine please reach out to @{user_handle} to provide assistance 👍\n\n")
        
        help_message = await context.bot.send_photo(chat_id=GROUP_ID,
                                                      photo=InputFile(bio, filename='boar.jpg'),
                                                      caption=message)
        
    except Exception as e:
        print("The exception is", e)
    
    return ROUTE

async def view_snake(update, context: ContextTypes.DEFAULT_TYPE):

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    # desired_width = 300  
    # desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(f'./images/snake.jpg', 'rb') as f:
        image = Image.open(f)
        # resized_image = image.resize((desired_width, desired_height))

        bio = io.BytesIO()
        # resized_image.save(bio, format='JPEG')
        image.save(bio,format='JPEG')
        bio.seek(0)

    # User Chat
    message = ("Give the snake space to retreat. Slowly move away from it without making sudden movements! \n\n"
               "Keep your pets on a tight leash to prevent them from chasing after the snake and potentially frightening it. \n\n"
               "We have reached out to the relevant experts, sit tight, help is on the way 👍\n\n")
    
    animal_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename='snake.jpg'),
                                                   caption=message,
                                                   reply_markup=reply_markup)

    context.user_data['animal_message'] = animal_message

    # Reset bio for the next use
    # Image Handling: The image is loaded and saved into an in-memory bio buffer, which is then used to send the image. The bio.seek(0) resets the buffer to the beginning, allowing it to be reused for the helper chat.
    bio.seek(0)

    # Helper chat
    try:
        user_handle = update.effective_user.username #assuming someone has a handle some people don't
        message = ("🚨 Someone has just spotted a Snake! 🚨\n\n"
                  f"@xyingxtingx please reach out to @{user_handle} to provide assistance 👍\n\n")
        
        help_message = await context.bot.send_photo(chat_id=GROUP_ID,
                                                      photo=InputFile(bio, filename='snake.jpg'),
                                                      caption=message)
        
    except Exception as e:
        print("The exception is", e)
    
    return ROUTE

async def view_monkey(update, context: ContextTypes.DEFAULT_TYPE):

    original_message = context.user_data['original_message']  # initialized during the start function
    await original_message.delete()

    # desired_width = 300  
    # desired_height = 200  

    keyboard = [
        [InlineKeyboardButton("< Back To Menu", callback_data="start"), ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    with open(f'./images/monkey.jpeg', 'rb') as f:
        image = Image.open(f)
        # resized_image = image.resize((desired_width, desired_height))

        bio = io.BytesIO()
        # resized_image.save(bio, format='JPEG')
        image.save(bio,format='JPEG')
        bio.seek(0)

    # User Chat
    message = ("If you need to pass by a lone macaque or a troop of macaques, walk by calmly without staring or maintaining eye contact! \n\n"
               "Refrain from feeding macaques. When they get used to being fed, they reduce their natural inclination to forage in the forest. \n\n"
               "We have reached out to the relevant experts, sit tight, help is on the way 👍\n\n")
    
    animal_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename='monkey.jpeg'),
                                                   caption=message,
                                                   reply_markup=reply_markup)

    context.user_data['animal_message'] = animal_message

    # Reset bio for the next use
    # Image Handling: The image is loaded and saved into an in-memory bio buffer, which is then used to send the image. The bio.seek(0) resets the buffer to the beginning, allowing it to be reused for the helper chat.
    bio.seek(0)

    # Helper chat
    try:
        user_handle = update.effective_user.username #assuming someone has a handle some people don't
        message = ("🚨 Someone has just spotted a Macaque! 🚨\n\n"
                  f"@Peanutezxc please reach out to @{user_handle} to provide assistance 👍\n\n")
        
        help_message = await context.bot.send_photo(chat_id=GROUP_ID,
                                                      photo=InputFile(bio, filename='monkey.jpeg'),
                                                      caption=message)
        
    except Exception as e:
        print("The exception is", e)
    
    return ROUTE

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # code below deletes users message to the bot
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    
    try:
        if context.user_data['unknown_message'] != None:
            unknown_message = context.user_data['unknown_message']
            await unknown_message.delete()
    except Exception as e:
        print("unknown message is not set")

    try:
        if context.user_data['original_message'] != None:
            original_message = context.user_data['original_message']
            await original_message.delete()
    except Exception as e:
        print("original message is not set")

    try:
        if context.user_data['animal_message'] != None:
            animal_message = context.user_data['animal_message']
            await animal_message.delete()
    except Exception as e:
        print("animal message is not set")

    unknown_message = await context.bot.send_message(
    chat_id=update.effective_chat.id,
    text="Sorry did not understand please use or press the /start command again" 
        )
    
    context.user_data['unknown_message'] = unknown_message

    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELE_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        fallbacks=[MessageHandler(filters.TEXT, unknown)],
        states = {
            ROUTE: {                
                CommandHandler('start', start),
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(view_otter, pattern="^view_otter$"),
                CallbackQueryHandler(view_boar, pattern="^view_boar$"),
                CallbackQueryHandler(view_snake, pattern="^view_snake$"),
                CallbackQueryHandler(view_monkey, pattern="^view_monkey$"),
            },
            })

    application.add_handler(conversation_handler)
    if os.getenv("WEBHOOK_URL"):
        application.run_webhook(listen="0.0.0.0",
                            port=int(PORT),
                            url_path=TELE_TOKEN,
                            webhook_url=os.getenv("WEBHOOK_URL") + TELE_TOKEN)
        logger.info("Application running via webhook: ", TELE_TOKEN)
    else:
        application.run_polling()
        logger.info("Application running via polling")