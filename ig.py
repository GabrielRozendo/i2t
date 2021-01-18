import os
from pathlib import Path
from datetime import datetime
import shutil
from instaloader import instaloader, Profile
from itertools import dropwhile, takewhile
import glob
import logging
from sender import Sender

logger = logging.getLogger()


class IG:
    def __init__(self):
        logger.debug('instaloader setup')

        user = os.getenv('IG_USER')
        password = os.getenv('IG_PASS')

        # instaloader -l i2t_bot
        self.L = instaloader.Instaloader()
        filename = os.path.join(os.getcwd(), 'session-i2t_bot')
        self.L.load_session_from_file(user, filename=filename)
        # self.L.login(user, password)
        self.L.post_metadata_txt_pattern = ''
        self.L.download_comments = False
        self.L.compress_json = False
        self.L.save_metadata = False
        self.L.download_video_thumbnails = False

    def __del__(self):
        self.L.close()

    def prepare_folder(self, name):
        folder = Path(name)
        if folder.exists() and folder.is_dir():
            shutil.rmtree(folder, ignore_errors=True)
            files = glob.glob('/name/*')
            for f in files:
                os.remove(f)
        logger.debug(f'folder {name} exists: {folder.exists()}')
        folder.mkdir(parents=True, exist_ok=True)

    def get_caption(self, post):
        users = post.tagged_users
        if users is not None and len(users) > 0:
            users = '\n@' + ' @'.join(users)
        else:
            users = ''

        if len(post.caption_hashtags) > 0:
            hashtags = '#' + ' #'.join(post.caption_hashtags)
        else:
            hashtags = ''

        date = post.date_local.strftime('%A, %d / %B / %Y %H:%M:%S')
        date = f'<code>{date}</code>\n\n'

        # TODO: Add emoji as prefix
        location = f'LOCAL: {post.location}\n\n' if post.location is not None else ''
        link = ''  # f'\n\n<i><a href="{post.url}">LINK</a></i>'

        message = f'{date}{location}{post.caption}{users}{link}'
        return message

    def update(self, u, last_time, username, channel):
        logger.debug(f'update instagram since {last_time} for user {username}')

        sender = Sender(channel)
        profile = Profile.from_username(self.L.context, username)

        if u.get('profile_pic_url', '') != profile.profile_pic_url:
            if sender.update_picture(profile.profile_pic_url):
                u['profile_pic_url'] = profile.profile_pic_url

        posts = list(takewhile(lambda p: p.date_utc >
                               last_time, profile.get_posts()))
        if len(posts) > 0:
            # sender.send_message(
            # f'{len(posts)} novos posts de {profile.full_name}')
            folder = profile.username
            self.prepare_folder(folder)
            posts.reverse()

            for post in posts:
                pattern = post.date_utc.strftime('%Y-%m-%d_%H-%M-%S*')
                result = self.L.download_post(post, folder)

                if result:
                    files_list = glob.glob(os.path.join(folder, pattern))
                    message = self.get_caption(post)
                    sender.send_message(message)

                    for file in files_list:
                        sender.send_file(file)
                        os.remove(file)

        for story_user in self.L.get_stories([profile.userid]):
            stories = list(
                filter(lambda s: s.date_utc > last_time, story_user.get_items()))

            if len(stories) > 0:
                # sender.send_message(
                # f'{len(stories)} stories ativos de {profile.full_name}')
                folder = f'{profile.username}_stories'
                self.prepare_folder(folder)

                for story in stories:
                    self.L.download_storyitem(story, folder)

                for file in os.listdir(folder):
                    f = os.path.join(folder, file)
                    sender.send_file(f)
                    os.remove(f)

        return True
