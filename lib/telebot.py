"""
Module Telebot
"""
import collections
import re
import telepot


class Telebot(telepot.Bot):
    """
    The Telebot class use a telepot bot.
    The management of the bot is done through the handle decorator
        Example:
            @bot.handler("/start")
            def on_start():
                bot.is_listen = True
                bot.sendMessage("Bot start")

            @bot.handler("/photo")
            def on_photo():
                bot.sendPhoto(camera.take_photo(), "photo")

    :param token_id : the token id
    """

    def __init__(self, token_id):
        super().__init__(token_id)
        self._handle = collections.defaultdict(list)
        self.message_loop(self._postreceive)
        self.chat_id = None
        self.command = None
        self._is_listen = False

    @property
    def is_listen(self):
        """
        Property bot status

        :return: True or False
        """
        return self._is_listen

    @is_listen.setter
    def is_listen(self, status):
        self._is_listen = status

    def handler(self, cmd):
        """
        Decorator to create the bot commands
        Add commands as a function in a dictionary

        :param cmd: command name
        """

        def decorator(func):
            self._handle[cmd].append(func)
            return func
        return decorator

    def _get_args(self):
        """
        retrieves the arguments of the command

        :return: tuples arguments
        """
        regex_args = re.compile('=(\w+|\d+)')
        regex_cmd = re.compile('^\/\w+')

        args = re.findall(regex_args, self.command)
        self.command = regex_cmd.search(self.command).group(0)
        return tuple(args)

    def _postreceive(self, msg):
        """
        callback for telepot.message_loop

        :param msg: message received
        """
        self.chat_id = msg['chat']['id']
        self.command = msg['text']

        args = self._get_args()

        for handle in self._handle.get(self.command, []):
            if args is not None:
                handle(*args)
            else:
                handle()
            return 0
        return 1

    def send_photo(self, file, msg):
        """
        Encapsulates the sendPhoto method

        :param file: photo to send
        :param msg: picture title
        """
        self.sendPhoto(self.chat_id, photo=open(file, 'rb'), caption=msg)

    def send_message(self, msg):
        """
        Encapsulates the sendMessage method

        :param msg: message to send
        """
        self.sendMessage(self.chat_id, str(msg))

    def send_video(self, video, msg):
        """
        Send the video if there are no errors in the recording, otherwise send the error message.

        :param video: a dictionary containing the name of the video,
                      the return code of the recording
                      and the error message if recording fail
        :param msg: video title
        """
        if video["return_code"] is None:
            super().sendVideo(self.chat_id, video=open(video["name"], 'rb'), caption=msg)
        else:
            super().sendMessage(self.chat_id, video["return_code"])
