import time
import os
import selenium.common.exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By

from modules.MovieDataObject import MovieData


DOCKER_CONTAINER = os.environ.get('DOCKER_CONTAINER', False)


class FilmWebScrapper:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
    
        if DOCKER_CONTAINER:
            self.driver = webdriver.Remote(
            command_executor='http://chrome:4444',
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
        except selenium.common.exceptions.NoSuchElementException:
            print("No cookies to accept")
            pass

    def get_first_page_watched_movies_from_filmweb(self, filmweb_user: str) -> list:
        """
        Get first page of watched movies from filmweb.

        :param filmweb_user: filmweb user name

        :return: list of MovieData objects with movies from filmweb
        """

        url = f"https://www.filmweb.pl/user/{filmweb_user}/films"
        movies_return = []

        print(url)

        try:
            self.driver.get(url)
        except Exception as e:
            print("Error while getting first page of watched movies from FilmWeb", e)
            return []

        time.sleep(5)

        h = 0.1
        while h < 9.9:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight/%s);" % h
            )
            h += 0.01

        time.sleep(3)

        print("Parsing movies from FilmWeb")

        movies = self.driver.find_element(
            By.XPATH, '//*[@id="site"]/div[3]/div/section[2]/section/div/div'
        )
        print("Movies parsed")

        print("Parsing movies from FilmWeb")
        movies_parsed = movies.find_elements(
            By.XPATH,
            '//div[@class="voteBoxes__box userVotesPage__result __FiltersResult animatedPopList__item"]',
        )
        print("Movies parsed")

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

                movie_poster_url = "https://kranus.pro/kranus.pro.gif"
                # movie_poster_url = movie.find_element(
                #     By.CLASS_NAME, "poster__image"
                # ).get_attribute("src")

                movie_user_rate = rendered_movies_rates[idx].text

                movie_url = movie.find_element(
                    By.CLASS_NAME, "preview__link"
                ).get_attribute("href")

                movie_user_opinion = (
                    movie.find_element(By.CLASS_NAME, "voteCommentText__label").text
                    if movie.find_element(By.CLASS_NAME, "voteCommentText__label")
                    else ""
                )

                movies_return.append(
                    MovieData(
                        movie_title=movie_title,
                        movie_year=movie_year,
                        movie_rating=movie_rating,
                        movie_id=movie_id,
                        movie_url=movie_url,
                        movie_poster_url=movie_poster_url,
                        user_rating=movie_user_rate,
                        user_text_opinion=movie_user_opinion,
                        rated_by=filmweb_user,
                    )
                )

        movies_return = movies_return[::-1]

        return movies_return
