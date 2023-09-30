import time
import os
import logging
import requests
import selenium.common.exceptions

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from modules.MovieDataObject import MovieData


DOCKER_CONTAINER = os.environ.get("DOCKER_CONTAINER", False)


class FilmWebScrapper:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")

        if DOCKER_CONTAINER:
            self.driver = webdriver.Remote(
                command_executor="http://chrome:4444",
                options=chrome_options,
            )
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.implicitly_wait(30)

        self.get_ready()

    def close_driver(self) -> None:
        """
        Close driver.
        """

        logging.debug("Closing driver")
        self.driver.quit()

    def get_ready(self) -> None:
        """
        Get ready for scrapping. (cookies)
        """

        self.driver.get("https://www.filmweb.pl/")

        try:
            self.driver.find_element(
                By.XPATH, '//*[@id="didomi-notice-agree-button"]'
            ).click()
            logging.debug("Cookies accepted")
        except selenium.common.exceptions.NoSuchElementException:
            logging.debug("No cookies to accept")
            pass

    def get_better_movie_poster(self, poster_url: str) -> str:
        """
        Get better movie poster from filmweb.

        :param poster_url: url to movie poster

        :return: url to better movie poster
        """

        if poster_url == "":
            return poster_url

        last_url_number = poster_url.split("/")[-1].split(".")[-2]
        last_url_number = "." + last_url_number + "."

        better_poster_url = poster_url.replace(last_url_number, ".3.")

        time.sleep(0.5)

        r = requests.head(poster_url)
        if r.status_code == 200:
            return better_poster_url
        else:
            return poster_url

    def scrape_additional_movie_data_from_url(self, filmweb_film_url: str) -> MovieData:
        """
        Scrapes movie data from filmweb for given film url.
        Scraped data:
            - Director
            - Scenarist

        :param filmweb_film_url: filmweb movie url

        :return: MovieData object with movie data
        """

        filmweb_film_url = filmweb_film_url.replace("http://", "https://")

        if "/film/" not in filmweb_film_url:
            return None

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0"
        }

        logging.debug(f"Scraping movie data from {filmweb_film_url}")

        r = None
        soup = None

        try:
            r = requests.get(filmweb_film_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            logging.error(e)
            return None

        if r.status_code != 200 or "Nie znaleziono strony" in r.text:
            return None

        multiple_creators = lambda x: ", ".join([i['title'] for i in x])

        movie_director = ""
        movie_scenarist = ""

        try:
            movie_director = (
                multiple_creators(soup.find("div", {"class": "filmPosterSection__info filmInfo"})
                .find("div", {"data-type": "directing-info"})
                .find_all("a"))
            )
            movie_scenarist = (
                multiple_creators(soup.find("div", {"class": "filmPosterSection__info filmInfo"})
                .find("div", {"data-type": "screenwriting-info"})
                .find_all("a"))
            )
        except Exception as e:
            logging.error(
                f"Error while parsing movie data from {filmweb_film_url}, failed to get director and scenarist: {e}"
            )
            pass

        scraped_movie = MovieData(
            movie_title="",
            movie_year=0,
            movie_rating=0.0,
            movie_id=0,
            movie_url="",
            movie_poster_url="",
            movie_director=movie_director,
            movie_scenarist=movie_scenarist,
            user_rating=0.0,
            user_text_opinion="",
            rated_by="",
        )

        return scraped_movie

    def get_first_page_watched_movies_from_filmweb(self, filmweb_user: str) -> list:
        """
        Get first page of watched movies from filmweb.

        :param filmweb_user: filmweb user name

        :return: list of MovieData objects with movies from filmweb
        """

        def isfloat(num):
            try:
                float(num)
                return True
            except ValueError:
                return False

        url = f"https://www.filmweb.pl/user/{filmweb_user}/films"
        movies_return = []

        logging.debug(f"Getting first page of movies from {url}")

        try:
            self.driver.get(url)
        except Exception as e:
            logging.error(e)
            return []

        time.sleep(5)

        h = 0.1
        while h < 9.9:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight/%s);" % h
            )
            h += 0.01

        time.sleep(3)

        logging.debug("Parsing movies from FilmWeb")

        movies = 0
        try:
            movies = self.driver.find_element(
                By.XPATH,
                '//div[@class="userVotesPage__results voteBoxes __FiltersResults animatedPopList __OwnerProfile isInited"]',
            )
        except Exception as e:
            logging.error(e)
            return []

        movies_parsed = movies.find_elements(
            By.XPATH,
            '//div[@class="voteBoxes__box userVotesPage__result __FiltersResult animatedPopList__item"]',
        )
        logging.debug(f"Found {len(movies_parsed)} movies - parsing succeded")

        rendered_movies_rates = movies.find_elements(
            By.XPATH, '//span[@class="userRate__rate"]'
        )

        for idx, movie in enumerate(movies_parsed):
            if (
                movie.get_attribute("class")
                == "voteBoxes__box userVotesPage__result __FiltersResult animatedPopList__item"
            ):
                movie_title = movie.find_element(By.CLASS_NAME, "preview__link").text
                movie_year = int(
                    movie.find_element(By.CLASS_NAME, "preview__year").text
                )

                movie_rating = (
                    float(
                        str(
                            movie.find_element(
                                By.CLASS_NAME, "communityRatings__value"
                            ).text
                        ).replace(",", ".")
                    )
                    if movie.find_element(By.CLASS_NAME, "communityRatings__value").text
                    != "-"
                    else 0.0
                )

                movie_id = movie.find_element(By.CLASS_NAME, "ribbon").get_attribute(
                    "data-id"
                )

                movie_url = movie.find_element(
                    By.CLASS_NAME, "preview__link"
                ).get_attribute("href")

                movie_poster_url = ""
                try:
                    movie_poster_url = movie.find_element(
                        By.CLASS_NAME, "poster__image"
                    ).get_attribute("src")
                except selenium.common.exceptions.NoSuchElementException:
                    logging.debug(f"No poster found for {movie_title} - skipping")
                    pass

                movie_poster_url = self.get_better_movie_poster(movie_poster_url)

                movie_user_rate = rendered_movies_rates[idx].text

                movie_url = movie.find_element(
                    By.CLASS_NAME, "preview__link"
                ).get_attribute("href")

                movie_user_opinion = (
                    movie.find_element(By.CLASS_NAME, "voteCommentText__label").text
                    if movie.find_element(By.CLASS_NAME, "voteCommentText__label")
                    else ""
                )

                if isfloat(movie_user_rate) is False:
                    continue

                movie_additional_data = self.scrape_additional_movie_data_from_url(
                    movie_url
                )

                movie_director = ""
                movie_scenarist = ""

                if movie_additional_data is not None:
                    movie_director = movie_additional_data.movie_director
                    movie_scenarist = movie_additional_data.movie_scenarist

                movies_return.append(
                    MovieData(
                        movie_title=movie_title,
                        movie_year=movie_year,
                        movie_rating=movie_rating,
                        movie_id=movie_id,
                        movie_url=movie_url,
                        movie_poster_url=movie_poster_url,
                        movie_director=movie_director,
                        movie_scenarist=movie_scenarist,
                        user_rating=movie_user_rate,
                        user_text_opinion=movie_user_opinion,
                        rated_by=filmweb_user,
                    )
                )

        movies_return = movies_return[::-1]

        return movies_return
