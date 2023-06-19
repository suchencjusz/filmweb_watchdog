import os
import time
import schedule

from dotenv import load_dotenv

from modules.FilmwebWatchod import FilmWebWatchdog
from modules.DiscordNotify import DiscordNotify


FILMWEB_USER = (
    load_dotenv("FILMWEB_USER")
    if load_dotenv("FILMWEB_USER")
    else os.getenv("FILMWEB_USER")
)
DISCORD_WEBHOOK_URL = (
    load_dotenv("DISCORD_WEBHOOK_URL")
    if load_dotenv("DISCORD_WEBHOOK_URL")
    else os.getenv("DISCORD_WEBHOOK_URL")
)
DISCORD_WEBHOOK_COLOR = (
    load_dotenv("DISCORD_WEBHOOK_COLOR")
    if load_dotenv("DISCORD_WEBHOOK_COLOR")
    else os.getenv("DISCORD_WEBHOOK_COLOR")
)
SCHEDULE_LOOP = (
    load_dotenv("SCHEDULE_LOOP")
    if load_dotenv("SCHEDULE_LOOP")
    else os.getenv("SCHEDULE_LOOP")
)
SCHEDULE_LOOP = True if SCHEDULE_LOOP == "True" else False


def main():
    fm_wchdg = FilmWebWatchdog(FILMWEB_USER)
    dc_notify = DiscordNotify(DISCORD_WEBHOOK_URL, DISCORD_WEBHOOK_COLOR)

    db_movies = fm_wchdg.get_all_watched_movies_from_db()
    filmweb_movies = fm_wchdg.get_all_watched_movies_from_filmweb()

    movies_not_in_db = fm_wchdg.compare_watched_movies(
        db_movies=db_movies, filmweb_movies=filmweb_movies
    )

    fm_wchdg.filmweb_scraper.close_driver()

    if len(movies_not_in_db) > 0:
        fm_wchdg.insert_multiple_data_to_db(movies_not_in_db)

        for movie in movies_not_in_db:
            dc_notify.notify(movie=movie)
    else:
        print("No new movies to add to database.")


if __name__ == "__main__":
    if SCHEDULE_LOOP:
        print("Schedule loop is on.")
        while True:
            schedule.every(2).minutes.do(main)
            schedule.run_pending()
            time.sleep(1)

    main()
