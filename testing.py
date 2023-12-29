from quart import Quart, render_template, redirect, session, url_for, request
from quart_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import os


app = Quart(__name__, template_folder='templates')
app.secret_key = 'AIzaSyClWALro4UavCzmrH3qxJwzRNM4W_Y3PcY'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
app.config["DISCORD_CLIENT_ID"] = '1176580752419344445'
app.config["DISCORD_CLIENT_SECRET"] = 'e4zYyVPWxRIg3nlPImMMY8KrXa02qIL8'
app.config["DISCORD_REDIRECT_URI"] = 'https://fudgy.darkside.com/callback'
app.config["DISCORD_BOT_TOKEN"] = 'MTE3NjU4MDc1MjQxOTM0NDQ0NQ.Gx32BX.iMKKMk7T0FPJAMHKeWw9tYOgi6Rx44gpHSfhpU'

# Specify the allowed Discord server ID and role ID
ALLOWED_SERVER_ID = '543535423046156288'
ALLOWED_ROLE_ID = '705366073154994207'

discordd = DiscordOAuth2Session(app)


@app.route("/")
async def home():
  logged = ""
  lst = []
  data = {}
  balance = 0
  if await discordd.authorized:
    logged = True
    user = await discordd.fetch_user()
  return await render_template("index.html", logged=logged)

@app.route("/login/")
async def login():
  return await discordd.create_session(scope=["identify", "guilds"])


@app.route("/logout/")
async def logout():
  discordd.revoke()
  return redirect(url_for(".home"))


@app.route("/me/")
@requires_authorization
async def me():
  user = await discordd.fetch_user()
  return redirect(url_for(".home"))


if __name__ == '__main__':
    app.run(debug=True)