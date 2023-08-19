from modules.FilmwebWatchod import FilmWebWatchdog
from modules.DiscordNotify import DiscordNotify
from modules.ConfigManager import ConfigManager


def main():
    config = ConfigManager("config.json").load()

    fm_watchdog = FilmWebWatchdog("hello")
    dc_notify = DiscordNotify(config["discord"]["webhook_url"], "ff0000")

    for user in config["users"]:
        fm_watchdog.change_user(user["name"])
        db_movies = fm_watchdog.get_all_watched_movies_from_db()
        filmweb_movies = fm_watchdog.get_all_watched_movies_from_filmweb()

        movies_not_in_db = fm_watchdog.compare_watched_movies(
            db_movies=db_movies, filmweb_movies=filmweb_movies
        )

        if len(movies_not_in_db) > 0:
            fm_watchdog.insert_multiple_data_to_db(movies_not_in_db)

            for movie in movies_not_in_db:
                dc_notify.notify(movie=movie)
        else:
            print("No new movies to add to database.")

    fm_watchdog.filmweb_scraper.close_driver()


if __name__ == "__main__":
    main()
