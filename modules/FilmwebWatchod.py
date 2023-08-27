import logging

from modules.DatabaseManager import DBManager
from modules.FilmWebScrapper import FilmWebScrapper


class FilmWebWatchdog:
    def __init__(self, filmweb_user: str):
        self.db_manager = DBManager(filmweb_user=filmweb_user)
        self.filmweb_scraper = FilmWebScrapper()
        self.filmweb_user = filmweb_user

    def change_user(self, filmweb_user: str) -> None:
        """
        Change user.

        :param filmweb_user: new filmweb user

        :return: None
        """

        self.filmweb_user = filmweb_user
        self.db_manager.filmweb_user = filmweb_user

    def get_all_watched_movies_from_db(self) -> list:
        """
        Get all watched movies from database.

        :return: list of tuples with movies from database
        """

        conn = self.db_manager.connect()
        c = conn.cursor()
        c.execute("SELECT * FROM %s" % self.filmweb_user)
        movies = c.fetchall()
        conn.close()
        return movies

    def insert_multiple_data_to_db(self, movie_data: list) -> None:
        """
        Insert multiple data to database.

        :param movie_data: list of MovieData objects with movies to insert to database

        :return: None
        """

        self.db_manager.insert_multiple_data_to_db(movie_data)

    def get_all_watched_movies_from_filmweb(self) -> list:
        """
        Get all watched movies from filmweb.

        :return: list of MovieData objects with movies from filmweb
        """

        return self.filmweb_scraper.get_first_page_watched_movies_from_filmweb(
            self.filmweb_user
        )

    def compare_watched_movies(self, db_movies: list, filmweb_movies: list) -> list:
        """
        Compare movies from database with movies from filmweb.

        :param db_movies: list of tuples with movies from database
        :param filmweb_movies: list of MovieData objects with movies from filmweb

        :return: list of MovieData objects with movies that are not in database
        """

        movies_to_add_to_db = []
        already_in_db_ids = [db_movie[1] for db_movie in db_movies]

        for filmweb_movie in filmweb_movies:
            if int(filmweb_movie.movie_id) in already_in_db_ids:
                logging.debug(
                    f"{filmweb_movie.movie_title} {filmweb_movie.movie_id} is already in the database"
                )

                continue

            movies_to_add_to_db.append(filmweb_movie)

        return movies_to_add_to_db
