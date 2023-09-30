import os
import sys
import time
import logging

from modules.FilmwebWatchod import FilmWebWatchdog
from modules.DiscordNotify import DiscordNotify
from modules.ConfigManager import ConfigManager

VERSION = "1.1.0"

logging.basicConfig(level=int(os.environ["LOG_LEVEL"]))
# logging.basicConfig(level=logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s", "%m-%d-%Y %H:%M:%S"
)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)


def main():
    config = ConfigManager("data/config.json").load()

    fm_watchdog = FilmWebWatchdog("hello")
    dc_notify = DiscordNotify(config["discord"]["webhook_url"])

    for user in config["users"]:
        logging.info(f"Checking user: {user['name']}")

        fm_watchdog.change_user(user["name"])
        db_movies = fm_watchdog.get_all_watched_movies_from_db()
        filmweb_movies = fm_watchdog.get_all_watched_movies_from_filmweb()

        movies_not_in_db = fm_watchdog.compare_watched_movies(
            db_movies=db_movies, filmweb_movies=filmweb_movies
        )

        if len(movies_not_in_db) > 0:
            fm_watchdog.insert_multiple_data_to_db(movies_not_in_db)

            for movie in movies_not_in_db:
                dc_notify.notify(movie=movie, embed_color=user["embed_color"])
                logging.warning(
                    f"New movie for user: {user['name']} - {movie.movie_title} {movie.movie_year} {movie.movie_rating} {movie.movie_id} {movie.movie_url} {movie.movie_poster_url} {movie.movie_director} {movie.movie_scenarist} {movie.user_rating} {movie.user_text_opinion} {movie.rated_by}"
                )
        else:
            logging.info(f"No new movies for user: {user['name']}")

    fm_watchdog.filmweb_scraper.close_driver()


if __name__ == "__main__":
    logging.info(f"Starting FilmWebWatchdog - {VERSION}")
    time.sleep(10)

    while True:
        main()
        logging.info("Sleeping for 6 hours")
        time.sleep(60 * 60 * 6) # temp solution
