class MovieData:
    def __init__(
        self,
        movie_title: str,
        movie_year: int,
        movie_rating: float,
        movie_id: int,
        movie_url: str,
        movie_poster_url: str,
        movie_director: str,
        movie_scenarist: str,
        user_rating: float,
        user_text_opinion: str,
        rated_by: str,
    ):
        self.movie_title = movie_title
        self.movie_year = movie_year
        self.movie_rating = movie_rating
        self.movie_id = movie_id
        self.movie_url = movie_url
        self.movie_poster_url = movie_poster_url
        self.movie_director = movie_director
        self.movie_scenarist = movie_scenarist
        self.user_rating = user_rating
        self.user_text_opinion = user_text_opinion
        self.rated_by = rated_by

    def __str__(self) -> str:
        return f"{self.movie_title} {self.movie_year} {self.movie_rating} {self.movie_id} {self.movie_url} {self.movie_poster_url} {self.movie_director} {self.movie_scenarist} {self.user_rating} {self.user_text_opinion} {self.rated_by}"
