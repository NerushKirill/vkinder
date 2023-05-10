from main_proj.main_1 import BotInterface
from config import COMMUNITY_TOKEN


def main():
    bot = BotInterface(COMMUNITY_TOKEN)
    bot.handler()


if __name__ == '__main__':
    main()
