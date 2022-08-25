from src.library import *

destination = f'{sys.path[0]}/'

def sort_resolutions(link):
    "sort stream order"
    global video_resolutions
    global videos
    video_resolutions = []
    videos = []

    for stream in link.streams.order_by('resolution'):
        video_resolutions.append(stream)
        videos.append(stream)

    return video_resolutions, videos

def build_menu(buttons,n_cols,header_buttons=None,footer_buttons=None):
    "build menu for listing streams"
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def getcover(link):
    "get cover of url link"
    global temp
    img_data = requests.get(link.thumbnail_url).content
    temp = tempfile.NamedTemporaryFile()
    with open(f'{temp.name}', 'wb') as handler:
        handler.write(img_data)

try:
    def video(update: Update, context: CallbackContext):
        "download video"
        global chat_id , i , button_list , streamslist
        
        link = YouTube(str(context.args[0]), on_progress_callback=on_progress)
        update.message.reply_text('processing video ....')
        chat_id = str(update.message.chat_id)
        sort_resolutions(link)
        button_list = []

        # Looping through the video_resolutions list to be displayed on the screen for user selection...
        i = 1
        for resolution in video_resolutions:

            # define callback data with int
            callback_data = i

            # append streams and for InlineKeyboardButton
            streamslist  = str(resolution).replace('<Stream:','').replace('mime_type=','').split('fps')[0]
            i += 1
            button_list.append(InlineKeyboardButton(str(streamslist), callback_data = callback_data))

        reply_markup=InlineKeyboardMarkup(build_menu(button_list,n_cols=1))
        update.message.reply_text(chat_id,reply_markup=reply_markup)

    def videoHandler(update: Update , context : CallbackContext):
        update.callback_query.answer()
        print(update.callback_query.data)

        ## log callback data
        # context.bot.send_message(chat_id=update.effective_chat.id, 
        #                      text='[handle_callback_query] callback data: ' + update.callback_query.data)

        if update.callback_query.data:
            out = videos[int(update.callback_query.data) - 1].download(output_path=destination)
            context.bot.send_document(chat_id, document=open(f'{out}', 'rb'), filename=f'{out}')
            os.remove(out)

    def audio(update: Update, context: CallbackContext):
        "download audio"
        link = YouTube(str(context.args[0]), on_progress_callback=on_progress)
        update.message.reply_text('processing audio ....')
        chat_id = str(update.message.chat_id)
        getcover(link)

        video = link.streams.filter(only_audio=True).first()
        out = video.download(output_path=destination)
        try:
            base, ext = os.path.splitext(out)
            os.rename(out, base)

            cmd = f"ffmpeg -y -loop 1 -i '{temp.name}' -i '{os.path.realpath(base)}' -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest 'out.mp4'"
            subprocess.check_output(cmd, shell=True)
            subprocess.call(cmd, shell=True)

            os.rename('out.mp4', base + '.mp3')
            os.remove(base)
            final = (base + '.mp3')

            temp.close()
            context.bot.send_document(chat_id, document=open(f'{os.path.realpath(final)}', 'rb'), filename=f'{os.path.realpath(final)}')
            os.remove(final)
        except subprocess.CalledProcessError:
            print('ffmpeg are not installed')
            exit(1)

    def getinfo(update: Update, context: CallbackContext):
        "get url info"
        link = YouTube(str(context.args[0]), on_progress_callback=on_progress)
        update.message.reply_text(f"""title : {link.title}
date : {link.publish_date}
image url : {link.thumbnail_url}
description : {link.description}
metadata : {link.metadata}
""")

    def gethelp(update: Update, context: CallbackContext):
        update.message.reply_text("""Following Options Are available: \n
/video download url with video
/audio download url with only audio
/info get youtube url info
/help show help""")

except exceptions.RegexMatchError:
    print('Enter valid video link')
except exceptions.AgeRestrictedError:
    print('Video is age restricted, and cannot be accessed without OAuth.')
except exceptions.LiveStreamError:
    print('Video is a live stream.')
except exceptions.VideoUnavailable:
    print('Base video unavailable error.')
