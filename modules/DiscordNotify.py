from discord_webhook import DiscordWebhook, DiscordEmbed
from modules.MovieDataObject import MovieData


class DiscordNotify:
    def __init__(self, webhook_url) -> None:
        self.webhook_url = webhook_url

    def notify(self, movie: MovieData, embed_color: str) -> None:
        """
        Send notification to discord webhook.

        :param movie: MovieData object with movie to send to discord webhook

        :return: None
        """

        embed = DiscordEmbed(title=movie.movie_title, url=movie.movie_url)

        embed.set_color(color=embed_color)
        embed.set_provider(name="Filmweb", url="https://www.filmweb.pl")
        embed.set_thumbnail(url=movie.movie_poster_url)
        embed.set_footer(text="Filmweb Watchdog")

        embed.add_embed_field(
            name="Rating", value=f"{self.start_emoji_counter(float(movie.movie_rating))}"
        )
        embed.add_embed_field(name="⭐", value=f"{movie.movie_rating}/10")

        embed.add_embed_field(name="", value="", inline=False)

        embed.add_embed_field(
            name=f"{movie.rated_by} rating",
            value=f"{self.start_emoji_counter(float(movie.user_rating))}",
        )
        embed.add_embed_field(name="⭐", value=f"{movie.user_rating}/10")

        if movie.user_text_opinion != "":
            embed.add_embed_field(
                name="Opinion", value=movie.user_text_opinion, inline=False
            )

        embed.add_embed_field(name="", value="", inline=False)

        embed.add_embed_field(name="Title", value=movie.movie_title)
        embed.add_embed_field(name="Year", value=movie.movie_year)
        embed.add_embed_field(name="ID", value=movie.movie_id)
        
        if movie.movie_director != "":
            embed.add_embed_field(name="Director", value=movie.movie_director)

        if movie.movie_scenarist != "":
            embed.add_embed_field(name="Scenarist", value=movie.movie_scenarist)
        
        embed.set_footer(text="Filmweb Watchdog • github.com/suchencjusz")
        embed.set_timestamp()

        webhook = DiscordWebhook(
            url=self.webhook_url, embeds=[embed], rate_limit_retry=True
        )
        webhook.execute()

    def start_emoji_counter(self, stars: float) -> str:
        """
        Convert float rating to emoji string.

        :param stars: float rating

        :return: emoji string
        """

        return_string = ""
        stars_int = int(stars)

        full = "🌕"
        near_full = "🌖"
        half = "🌗"
        near_zero = "🌘"
        zero = "🌑"

        t = 10 - stars_int

        for i in range(0, stars_int):
            return_string += full

        difference = stars - float(stars_int)

        if difference >= 0.7:
            return_string += near_full
            t = t - 1
        elif difference >= 0.3:
            return_string += half
            t = t - 1
        elif difference > 0:
            return_string += near_zero
            t = t - 1

        for i in range(0, t):
            return_string += zero

        return return_string
