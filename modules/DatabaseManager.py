import sqlite3


class DBManager:
    def create_database(self) -> None:
        conn = sqlite3.connect("db/database.db")
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS user_watched_movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER
        )"""
        )

        conn.commit()
        conn.close()

    def connect(self) -> sqlite3.Connection:
        """
        Connect to database.

        :return: sqlite3.Connection object
        """

        self.create_database()
        return sqlite3.connect("db/database.db")

    def insert_one_movie_to_db(self, movie_id: int) -> None:
        """
        Insert one movie to database.

        :param movie_id: id of movie to insert to database

        :return: None
        """

        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT INTO user_watched_movies (movie_id) VALUES (?)", (movie_id,))
        conn.commit()
        conn.close()

    def insert_multiple_data_to_db(self, movie_data: list) -> None:
        """
        Insert multiple data to database.

        :param movie_data: list of MovieData objects with movies to insert to database

        :return: None
        """

        for movie in movie_data:
            self.insert_one_movie_to_db(movie.movie_id)
            print(f"Added {movie.movie_title} {movie.movie_id} to database")
        print(f"All movies added to database {len(movie_data)}")
