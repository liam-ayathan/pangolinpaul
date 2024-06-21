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

load_dotenv() #important!

# Loggerdea
logger = logging.getLogger(__name__)

# Telegram
TELE_TOKEN = os.getenv("TELE_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

PORT = int(os.environ.get('PORT', 5000))
ROUTE, REPORT_DESCRIPTION, REPORT_PHOTO, REPORT_FINAL = range(4) # defining different states

async def start(update, context: ContextTypes.DEFAULT_TYPE):
    
    context.user_data['injured'] = "" # adding this to reset injured status
    
    context.user_data['photo_path'] = None # adding this here in the event the user sends out multiple request for photo taking, meaning that we have to keep resetting the photo path when he returns to start

    keyboard = [
        [InlineKeyboardButton("Monitor Lizard 🦎", callback_data="view_board_monitor"),InlineKeyboardButton("Otter 🦦", callback_data="view_board_otter")],
        [InlineKeyboardButton("Wild Boar 🐗", callback_data="view_board_boar"),InlineKeyboardButton("Snake 🐍", callback_data="view_board_snake")],
        [InlineKeyboardButton("Bird 🐤", callback_data="view_bird"),InlineKeyboardButton("Others 🦘", callback_data="make_report_others")],
        # [InlineKeyboardButton("Others 🦘", callback_data="make_report_others")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = ("🎉 Hey there! Pangolin Paul here 👋\n\n"
               "I'm happy to help you if you need any Wildlife Assistance!\n\n"
               "Please select one of the relevant options below\n\n"
               "🚨 _For extremely urgent help please call __NParks’ Animal Response Centre (1800-476-1600)__ or __ACRES (9783-7782)___ 🚨")
    
    if update.callback_query:
        try: # for some reason if there is a callback, need to investigate this further - I shouldn't need this try block - Yes I do from view animal
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
          print(e)
          if context.user_data['original_message'] != None:
              original_message = context.user_data['original_message']
          start_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
          context.user_data['original_message'] = start_message
          try:
              await original_message.delete()
          except Exception as e:
              print(e)
    else: # if we are editing the previous message in the if statement, we won't delete the start message, otherwise we will edit it as seen here

        try:
            if context.user_data['original_message'] != None:
                original_message = context.user_data['original_message']
                await original_message.delete()
        except Exception as e:
            print("original start message is not set")

        start_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        context.user_data['original_message'] = start_message

    # try:
    #     if context.user_data['unknown_message'] != None:
    #         unknown_message = context.user_data['unknown_message']
    #         await unknown_message.delete()
    # except Exception as e:
    #     print("unknown message is not set")

    try:
        if context.user_data['animal_message'] != None:
            animal_message = context.user_data['animal_message']
            await animal_message.delete()
    except Exception as e:
        print("animal message is not set")

    try:
        if context.user_data['original_message'] != None:
            start_message = context.user_data['original_message']
            print("start message is set")
    except Exception as e:
        print("start message is not set")

    # code below deletes users message to the bot
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return ROUTE

async def view_board(update, context: ContextTypes.DEFAULT_TYPE):
    original_message = context.user_data['original_message']
    if update.callback_query:
            query = update.callback_query
            await query.answer()

            animal = query.data.split("_")[-1] # basically it will be called as make_report_{animalname}
            context.user_data['animal'] = animal
      
    if animal == "monitor":
        animal_text = "monitor lizard"
    else:
        animal_text = animal

    message = (f"You have selected *{animal_text}*!\n\n"
               "Please choose the relevant options below")
    
    if animal == "mynah" or animal == "koel":
        callback = "view_bird"
    else:
        callback = "start"
    
    keyboard = [
        [InlineKeyboardButton("Common Scenarios ❓", callback_data=f"view_animal_{animal}")],
        [InlineKeyboardButton("Injured Animal 🏥", callback_data=f"make_report_injured_{animal}"),],
        [InlineKeyboardButton("Contact Expert 👨‍🔬", callback_data=f"make_report_{animal}"),],
        [InlineKeyboardButton("Back", callback_data=callback),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e: 
        print("Message coming from view animal, original message was deleted ",e)
        original_message = context.user_data['original_message']
        start_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        context.user_data['original_message'] = start_message

        try:
            await original_message.delete() # deleting the photo message
        except Exception as e:
            print("Returning from view animal, cannot delete original message")

    return ROUTE

async def view_animal(update, context: ContextTypes.DEFAULT_TYPE):
    original_message = context.user_data['original_message']

    if update.callback_query:
            query = update.callback_query
            await query.answer()

            animal = query.data.split("_")[-1] # basically it will be called as make_report_{animalname}
            context.user_data['animal'] = animal

    with open(f'./images/{animal}.jpg', 'rb') as f:
        image = Image.open(f)
        # resized_image = image.resize((desired_width, desired_height))
        bio = io.BytesIO()
        # resized_image.save(bio, format='JPEG')
        image.save(bio,format='JPEG')
        bio.seek(0)

    # Setting the animal Messages

    if animal == "monitor":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*What to do when encountering monitor lizards in urban areas?*\n"
            "_Keep calm. Monitor lizards are generally shy and will not attack unless provoked. You can proceed to observe it from a safe distance._\n\n"
            "*What to do if I am bitten by a monitor lizard?*\n"
            "_In the very unlikely case that you get bitten, seek medical attention immediately. While their venom is not lethal to humans, their bite can cause infections._\n\n"
            # "*How do I prevent monitor lizards from entering my house?*\n"
            # "_Practise proper food waste disposal. Seal up holes and gaps in your property which monitor lizards might enter from or hole up in (e.g. under pool decks or other cool crevices). Prune trees and overhanging branches to restrict access into your property. Some monitor lizards are excellent climbers._\n\n"
            "If you need more assistance please press back"
        )

    if animal == "otter":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*What to do when encountering otters in urban areas?*\n"
            "_If you encounter otters, do not touch, chase or corner them. Instead, observe them from a distance as going too close may frighten them. Do not talk loudly and do not use flash photography. Noise and light may scare and provoke the otters._\n\n"
            "*How do I prevent otters from entering my house?*\n"
            "_Block off entry points so that otters cannot enter. Wire mesh, panels, modifying the gates/fences to make the gaps smaller are some methods that have been implemented and have been proven to be effective. Fencing off ponds and using netting to cover ponds are also possible measures._\n\n"
            "If you need more assistance please press back"
        )

    if animal == "boar":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*What to do when encountering wild boars in urban areas?*\n"
            "_Proper food waste management must be practised by disposing trash properly to discourage wild boars from scavenging._ \n\n"
            # "Additionally, ensure that fences are made from study material like galvanised steel and are properly maintained with a solid concrete base that is dug into the ground to prevent them from entering your property._\n\n"
            "*What to do when encountering wild boars in wild areas?*\n"
            "_If you are walking by with food, store it properly inside your bag instead of carrying it openly in plastic bags as they have learned to associate plastic bags with food. Avoid any actions that may startle or provoke them such as sudden movements, flash photography and loud noises._\n\n"
            # "_If you see a wild boar while walking your dog, please keep your dog on a tight leash and avoid going anywhere near the wild boar._\n\n"
            "If you need more assistance please press back"
        )

    if animal == "snake":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*What to do when encountering snakes in urban areas?*\n"
            "_Snakes are usually seen in urban areas due to the availability of food and shelter. Keep all family members and pets away from where the snake is. If a snake is found inside a room, keep all doors and windows that lead outside open for the snake to exit. Find out why the snake came to your area - a potential cause could be improper waste disposal which attracts pests that snakes prey on._\n\n"
            "*What to do when encountering snakes in wild areas?*\n"
            "_Observe from a safe distance, as snakes will not attack unless disturbed or provoked. Stay calm and back away slowly, giving the snake space to retreat. Do not approach or attempt to handle the snake._\n\n"
            "If you need more assistance please press back"
        )

    if animal == "monkey":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*What do I do when I encounter a macaque?*\n"
            "_Keep your distance and avoid direct eye contact as you pass by! Maintain a neutral expression as smiling at macaques is seen as a threatening gesture. _\n\n"
            "*What can I do to keep macaques from venturing into urban areas?*\n"
            "_Dispose of your trash appropriately and avoid feeding the macaques. Macaques have plenty of food in their forest habitats which include fruits and even small animals like lizards!_\n\n"
            "If you need more assistance please press back"
        )

    if animal == "mynah":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*What to do when encountering Mynahs in urban areas?*\n"
            "_The presence of Mynahs in your estate might be attributed to factors such as illegal feeding and excess food scraps lying around. Keep your estate clean by disposing your food waste properly!_\n\n"
            "*Where do Mynahs come from?*\n"
            "_Did you know that the Mynahs commonly found in Singapore are Javan Mynahs which were once endemic to Java and Bali? They were bought over to Singapore as part of the bird trade and outcompeted their other Mynah relatives, the Common and Hill Mynah, to be the most dominant Mynah species in Singapore._\n\n"
            "If you need more assistance please press back"
        )

    if animal == "koel":
        message = (
            "Below are some useful FAQs that could help!\n\n"
            "*Why are Koels so noisy?*\n"
            "_The 'uwu' sounds you hear are the male Koels calling for mates, during the breeding season which spans from October to March!_\n\n"
            "*What can I do about the noise?*\n"
            "_The Asian Koels are a protected species under the Wildlife Act. To minimise the inconvenience of their calls to residents, NParks and Town Councils prune trees, remove food sources and manage Crows nests to prevent Koels from roosting near your residential estates. _\n\n"
            "*What role do Koels play in our native ecosystem?*\n"
            "_Did you know that in Singapore, Asian Koels are brood parasites of the House Crow? This means that Female Asian Koels lay their eggs in unattended Crow nests. The Koel chick hatches first and may force the Crow's eggs or chicks out of the nest. This brood parasitism relationship thus help keep the Crow's population in check by reducing their reproduction success!_\n\n"
            "If you need more assistance please press back"
        )

    keyboard = [
        [InlineKeyboardButton("Back", callback_data=f"view_board_{animal}"),],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    scenario_message = await context.bot.send_photo(chat_id=update.effective_chat.id,
                                                   photo=InputFile(bio, filename=f'{animal}.jpg'),
                                                   caption=message,
                                                   parse_mode="Markdown",
                                                   reply_markup=reply_markup)
    
    context.user_data['scenario_message'] = scenario_message

    await original_message.delete()

    return ROUTE

async def view_bird(update, context: ContextTypes.DEFAULT_TYPE):
    original_message = context.user_data['original_message']
    pass
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        keyboard = [
            [InlineKeyboardButton("Mynah", callback_data="view_board_mynah"),InlineKeyboardButton("Koel", callback_data="view_board_koel")],
            [InlineKeyboardButton("Other Bird 🐔",callback_data="make_report_bird"),InlineKeyboardButton("Back",callback_data="start")],
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = ("Hey!\n\n"
                   "Choose the relevant bird 🐤 from the list below!")
        try:
            await query.edit_message_text(
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print("Callback triggered from view animal, which is a caption via send photo and cannot be edited",e)
            start_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            context.user_data['original_message'] = start_message
            await original_message.delete()
    
    return ROUTE

async def make_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['photo_path'] = None
    original_message = context.user_data['original_message']

    if update.callback_query:
        query = update.callback_query
        await query.answer()

        animal = query.data.split("_")[-1] # basically it will be called as make_report_{animalname}
        context.user_data['animal'] = animal 

        injured = query.data.split("_")[-2] # basically if this call came from an injured button it will be make_report_injured_{animalname}
        if injured == "injured":
            injured_status = "_Injured: Yes_\n\n"
            injured_text="that is *injured* 🏥"
        else:
            injured_status = ""
            injured_text=""
        context.user_data['injured'] = injured_status
        if animal == "bird":
            callback = "view_bird"
        elif animal != "others":
            callback = f"view_board_{animal}"
        else:
            callback = "start"

        keyboard = [
            [InlineKeyboardButton("Take a Photo 📷", callback_data="receive_photo"),],
            [InlineKeyboardButton("Continue without Photo 🏃", callback_data="write_description"),],
            [InlineKeyboardButton("Back", callback_data=callback),]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        if animal == "monitor":
            animal = "monitor lizard" #extend the name

        if animal != "others":
            animal_text = f"You are currently reporting on a *{animal}* {injured_text}\n\n"
        else:
            animal_text=""

        message = ("To better help you please provide us with more details of the situation! 📝\n\n"
                   f"{animal_text}"
                  # "The first step is to snap a picture 📷, please press _Snap Photo_\n\n"
                  # "If you don't want to take a picture, press _Continue without Photo_\n\n"
                  "If you don't want to make a report, please press back")
        try:
            await query.edit_message_text(
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        except Exception as e:
            print("Report was made through view animal, which is a caption via send photo and cannot be edited ",e)
            start_message = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            context.user_data['original_message'] = start_message
            await original_message.delete()
    return REPORT_PHOTO

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animal = context.user_data['animal']
    injured_status = context.user_data['injured']

    if injured_status != "": # animal is injured
        injured = "_injured"
    else: # animal is not injured
        injured = ""

    keyboard = [
        [InlineKeyboardButton("Back", callback_data=f"make_report{injured}_{animal}"),]
        # if animal is injured -> make_report_injured_{animal}
        # if animal is not injured -> make_report_{animal}
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = ("To better help you please snap a picture or provide us with a photo of the situation! 📷\n\n"
              "Otherwise, please press back to return to a previous screen")
    
    try:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    except Exception as e: # there is still an update since we are returning the same state, return_photo, but the original message has already been deleted
        print("Message coming from process image, original message was deleted ",e)
        original_message = context.user_data['original_message']
        start_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        context.user_data['original_message'] = start_message
        await original_message.delete() # deleting the photo message
        
    return REPORT_PHOTO

async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animal = context.user_data['animal']
    original_message = context.user_data['original_message']

    try:
        # Get the highest resolution photo
        sent_message = update.message
        photo = update.message.photo[-1]
        photo_path = photo.file_id
        context.user_data['photo_path'] = photo_path
        # file = await context.bot.get_file(file_id)
    except Exception as e:
        print("We are being directed here immediately because a photo has already been set, going back here from write description",e)
        photo_path = context.user_data['photo_path']
        sent_message = None

    if animal == "monitor":
        animal = "monitor lizard" #extend the name

    if animal != "others":
        animal_text = f"Image should capture a *{animal}*\n\n"
    else:
        animal_text=""
    
    # Define the caption text
    caption = ("This is the image you sent 📷!\n\n" 
               f"{animal_text}"
                # "If you would like to change the photo 📷, just snap another one and send it to us\n\n"
                # "If you would like to finish the report, just press *Finalise Report* below\n\n"
                "If you would like to go back to review changes or return to a previous screen, press back\n\n"
                )

    # Create the inline keyboard
    keyboard = [
        [InlineKeyboardButton("Write Description ✏️", callback_data="write_description"),],
        [InlineKeyboardButton("Back", callback_data="receive_photo"),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the photo back with the caption and the inline keyboard
    image_message = await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=photo_path,
        caption=caption,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    context.user_data['original_message'] = image_message
    await original_message.delete()

    # Deleting the sent image message to the chat (photo)
    if sent_message != None:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return REPORT_PHOTO

async def write_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animal = context.user_data['animal']
    original_message = context.user_data['original_message']

    photo_path = context.user_data['photo_path'] #could be None

    if photo_path != None: # they snapped a photo so they go back to see their photo
        back_callback = "process_image"
    else: # They didn't snap a photo so go back to make report
        injured_status = context.user_data['injured']

        if injured_status != "": # animal is injured
            injured = "_injured"
        else: # animal is not injured
            injured = ""
        back_callback = f"make_report{injured}_{animal}"

    keyboard = [
        [InlineKeyboardButton("Back", callback_data=f"{back_callback}"),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if animal == "monitor":
        animal = "monitor lizard" #extend the name

    if animal != "others":
        animal_text = f"_, Selected Animal is_ *{animal}*"
    else:
        animal_text=""

    message = ("To proceed please write a description of the situation you are in ✍️! Things to write include:\n\n"
              "_(1) Location_ 🌎\n\n"
              f"_(2) Animal(s) involved_ 🐵{animal_text}\n\n"
              "_(3) Details - Injury / Animal Behaviour / Current Situation_ 📜\n\n"
              "Otherwise, please press back to return to a previous screen")
        
    start_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    context.user_data['original_message'] = start_message
    
    await original_message.delete() # moved this down so that we are not stuck with completely no message

    return REPORT_DESCRIPTION

async def process_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        description = update.message.text
        sent_message = update.message
        context.user_data['description'] = description
    except Exception as e:
        print("user never sent a message and is returning from sending a photo or failing to ", e)
        description = context.user_data['description']
        sent_message = None

    original_message = context.user_data['original_message'] # I am resetting this message in the below code so I store this original message first, then I delete it later down the line
    animal = context.user_data['animal'] # setting the animal
    injured_status = context.user_data['injured']

    if sent_message != None and sent_message.text == "/start":
        keyboard = [
            [InlineKeyboardButton("Back to Menu", callback_data="start"),]
        ]
        message = ("If you would like to go back to the main menu please press the button below")

        reply_markup = InlineKeyboardMarkup(keyboard)
        start_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup
            )
        context.user_data['original_message'] = start_message
    else:
        
        # if context.user_data['photo_path'] != None: #photo is already set, don't need them to edit again
        #     proceed_callback = "process_image"
        # else:
        #     proceed_callback = "receive_photo"

        # if animal == "bird":
        #     callback = "view_bird"
        # elif animal != "others":
        #     callback = f"view_animal_{animal}"
        # else:
        #     callback = "start"

        keyboard = [
            [InlineKeyboardButton("Finalise Report 👍", callback_data="finalise_report")],
            # [InlineKeyboardButton("Edit Message ✏️", callback_data=f"make_report_{animal}")],
            [InlineKeyboardButton("Back", callback_data="write_description")]
        ]
        # message = "This is the description you send below: \n\n *Type: %s*\n\n *%s*\n\n If its accurate please proceed finish the report or add a supporting photo, if not please press back \n\n" % (animal,description)
        if animal == "monitor":
            animal = "monitor lizard" #extend the name

        message = ("This is the description you sent below: \n\n"
                   f"_Animal: {animal}_\n\n{injured_status}" # will be this "_Injured: Yes_\n\n" if active
                   f"_Description: {description}_\n\n"
                   "If its accurate please press proceed to finish the report, if not please press back \n\n")
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        start_message = await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        context.user_data['original_message'] = start_message
    
    await original_message.delete() # moved this down so that we are not stuck with completely no message

    # Deleting the sent message to the chat
    if sent_message != None: # if we are not returning from receive photo
        chat_id = sent_message.chat_id
        message_id = sent_message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    return REPORT_DESCRIPTION


async def finalise_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_path = context.user_data['photo_path'] #could be None
    description = context.user_data['description']
    animal = context.user_data['animal']
    injured_status = context.user_data['injured']

    original_message = context.user_data['original_message']

    keyboard = [
        [InlineKeyboardButton("Send Report ✅", callback_data=f"send_report")],
        [InlineKeyboardButton("Back", callback_data=f"process_description")]
    ]
    # message = "This is the description you send below: \n\n *Type: %s*\n\n *%s*\n\n If its accurate please proceed finish the report or add a supporting photo, if not please press back \n\n" % (animal,description)
    user_handle = update.effective_user.username

    if animal == "monitor":
        animal = "monitor lizard" #extend the name

    message = (f"_Reporter: @{user_handle}_\n\n"
                f"_Animal: {animal}_\n\n{injured_status}" # will be this "_Injured: Yes_\n\n" if active
                f"_Description: {description}_\n\n" 
                # "Above is the sample report that we will be sending our community experts\n\n"
                # "Don't worry if the reporter is listed as *None*, we will still be able to get back to you!\n\n"
                # "If the report is good to go please press proceed to send it out\n\n"
                "If you like to edit the report description and picture or return to a previous screen, please press back\n\n")
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if photo_path != None:
        image_message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_path,
            caption=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        context.user_data['original_message'] = image_message
    else:
        start_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        context.user_data['original_message'] = start_message

    await original_message.delete()

    return REPORT_FINAL

async def send_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Message sent to the Experts

    photo_path = context.user_data['photo_path'] #could be None
    description = context.user_data['description']
    animal = context.user_data['animal']
    injured_status = context.user_data['injured']

    user_id = update.effective_user.id
    user_handle = update.effective_user.username

    keyboard = [
        [InlineKeyboardButton("Respond Now!", url=f"tg://user?id={user_id}")]
    ]

    if animal == "monitor":
        animal = "monitor lizard" #extend the name

    user_handle = update.effective_user.username
    message = ( "🚨 Someone has just made a report! 🚨\n\n"
                f"_Reporter: @{user_handle}_\n\n"
                f"_Animal: {animal}_\n\n{injured_status}" # will be this "_Injured: Yes_\n\n" if active
                f"_Description: {description}_\n\n")
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if photo_path != None:
            help_message = await context.bot.send_photo(
                chat_id=GROUP_ID,
                photo=photo_path,
                caption=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )

        else:
            help_message = await context.bot.send_message(
                chat_id=GROUP_ID,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    except Exception as e:
        print("An exception occured when sending report ",e)

    # Message sent to the User Below

    original_message = context.user_data['original_message']

    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data=f"start")]
    ]

    message = ( "🚨 The Report has been sent! 🚨\n\n"
                f"_Reporter: @{user_handle}_\n\n"
                f"_Animal: {animal}_\n\n{injured_status}" # will be this "_Injured: Yes_\n\n" if active
                f"_Description: {description}_\n\n"
                "_Please give our experts between 15 minutes and an hour to get back to you ⏰. Your patience is greatly appreciated 👍_\n\n"
                "")
  
    reply_markup = InlineKeyboardMarkup(keyboard)

    if photo_path != None:
        report_message = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_path,
            caption=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        report_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

    context.user_data['report_message'] = report_message   

    await original_message.delete()

    return REPORT_FINAL

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        if context.user_data['original_message'] != None:
            start_message = context.user_data['original_message']
            await start_message.delete()
    except Exception as e:
        print("original start message is not set")

    try:
        if context.user_data['animal_message'] != None:
            animal_message = context.user_data['animal_message']
            await animal_message.delete()
    except Exception as e:
        print("animal message is not set")

    # Create the inline keyboard
    keyboard = [
        [InlineKeyboardButton("Back to Main Menu", callback_data="start"),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    unknown_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry did not understand or something went wrong, please use the button below to return to the main menu",
        reply_markup=reply_markup
        )
    
    context.user_data['original_message'] = unknown_message

    # code below deletes users message to the bot
    message = update.message
    if message != None:
        chat_id = message.chat_id
        message_id = message.message_id
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)

    # return ConversationHandler.END
    return ROUTE

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELE_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        fallbacks=[
            # MessageHandler('start', start),
            MessageHandler(filters.TEXT, unknown),
            MessageHandler(filters.PHOTO, unknown)],
            # I may also want to add a filters for stickers, because the message.update can send stickers
        states = {
            ROUTE: {                
                CommandHandler('start', start),
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(view_board, pattern="^view_board_(.*)$"),
                CallbackQueryHandler(view_animal, pattern="^view_animal_(.*)$"),
                CallbackQueryHandler(view_bird, pattern="^view_bird$"),
                CallbackQueryHandler(make_report, pattern="^make_report_(.*)$"),
            },
            REPORT_PHOTO :{
                CommandHandler('start', start),
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(view_board, pattern="^view_board_(.*)$"),
                CallbackQueryHandler(view_bird, pattern="^view_bird$"),
                CallbackQueryHandler(make_report, pattern="^make_report_(.*)$"),
                CallbackQueryHandler(receive_photo, pattern="^receive_photo$"),
                CallbackQueryHandler(write_description, pattern="^write_description$"), # when going to process description from receive_photo
                MessageHandler(filters.PHOTO, process_image),
            },
            REPORT_DESCRIPTION: {
                CommandHandler('start', start),
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(make_report, pattern="^make_report_(.*)$"), #if the photo is not set, we go back directly here
                CallbackQueryHandler(process_image, pattern="^process_image$"),
                CallbackQueryHandler(write_description, pattern="^write_description$"),
                MessageHandler(filters.TEXT, process_description),
                CallbackQueryHandler(finalise_report, pattern="^finalise_report$"),
            },
            REPORT_FINAL :{
                CommandHandler('start', start),
                CallbackQueryHandler(start, pattern="^start$"),
                CallbackQueryHandler(process_description, pattern="^process_description$"),
                CallbackQueryHandler(finalise_report, pattern="^finalise_report$"),
                CallbackQueryHandler(send_report, pattern="^send_report$"),
            }
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