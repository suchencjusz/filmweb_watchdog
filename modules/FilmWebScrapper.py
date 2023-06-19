import time
import selenium.common.exceptions

from selenium import webdriver
from selenium.webdriver.common.by import By
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.chrome.service import Service as ChromeService

from webdriver_manager.chrome import ChromeDriverManager

from modules.MovieDataObject import MovieData


class FilmWebScrapper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("--log-level=3")
        options.add_argument("--blink-settings=imagesEnabled=false")

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

        # time.sleep(10)
        # self.driver = webdriver.Remote(
        #     command_executor='http://selenium:4444/wd/hub',
        #     options=options
        # )
        # time.sleep(10)

        self.driver.implicitly_wait(60)

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

        movies = self.driver.find_element(
            By.XPATH, "/html/body/div[6]/div[4]/div/section[2]/section/div/div"
        )
        movies_parsed = movies.find_elements(
            By.XPATH,
            '//div[@class="voteBoxes__box userVotesPage__result __FiltersResult animatedPopList__item"]',
        )

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

                movie_poster_url = movie.find_element(
                    By.CLASS_NAME, "poster__image"
                ).get_attribute("src")

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

        return movies_return
