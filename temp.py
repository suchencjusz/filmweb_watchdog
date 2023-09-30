import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

filmweb_film_url = "https://www.filmweb.pl/film/Pirania+II%3A+Lataj%C4%85cy+mordercy-1981-996"

try:
    r = requests.get(filmweb_film_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
except Exception as e:
    print(e)
#     return None

# if r.status_code != 200 or "Nie znaleziono strony" in r.text:
#     return None

movie_director = ""
movie_scenarist = ""

# try:

multiple_creators = lambda x: ", ".join([i['title'] for i in x])

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

print(movie_director,"-", movie_scenarist)