import logging
import os
import telegram
import requests

logger = logging.getLogger()


class Sender:
    def __init__(self, channel):
        self.channel = channel
        token = os.getenv('TBOT_TOKEN')
        self.bot = telegram.Bot(token=token)

    def update_picture(self, img_url):
        file_name = 'profile_picture'

        try:
            r = requests.get(img_url)

            with open(file_name, 'wb') as f:
                f.write(r.content)
            input_file = telegram.InputFile(
                open(file_name, 'rb'), attach=False)

            self.bot.set_chat_photo(self.channel, input_file)
            logger.info('Profile picture updated')
            return True

        except Exception as e:
            logger.error(f'Error on update profile picture: {e}')
            return False

        finally:
            os.remove(file_name)

    def send_message(self, text):
        if text is not None:
            logger.debug(text)

            # bot.send_message(chat_id=channel,
            #     text=r'*bold* _italic_ `fixed width font` [link](http://google.com)\.',
            #     parse_mode=telegram.ParseMode.MARKDOWN_V2)
            self.bot.send_message(chat_id=self.channel,
                                  text=text,
                                  parse_mode=telegram.ParseMode.HTML,
                                  disable_web_page_preview=True)

    def send_file(self, file):
        logger.debug(file)
        input_file = telegram.InputFile(open(file, 'rb'), attach=True)
        if file.lower().endswith('.mp4'):
            logger.debug('send video')
            # media.append(telegram.InputMediaVideo('video', input_file))
            self.bot.send_video(chat_id=self.channel, video=input_file)
            # context.bot.sendVideo(chat_id=chat_id, video=open(os.path.join(
            #     'cocatechpod_stories', file), 'rb'), caption="This is the test photo caption")
        else:
            # media.append(telegram.InputMediaPhoto('photo', input_file))
            logger.debug('send photo')
            self.bot.send_photo(chat_id=self.channel, photo=input_file)
            # bot.send_media_group(chat_id=channel, media=media)
