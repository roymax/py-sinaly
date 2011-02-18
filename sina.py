import web
from web.contrib.template import render_jinja
from sinat import Sinat, OAuthToken, OAuthConsumer 

CONSUMER_KEY = '3892402622' # your App Key
CONSUMER_SECRET = '6af8bdaa10fb55fa82089a8a29787f81' # your App Secret

urls = (
	"/" , "index",
	"/auth", "sinauth",
	"/auth/callback", "sina_callback"
)

sina_app = web.application(urls,locals())

render = render_jinja(
        'views',   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
    )  

class index:
	"""docstring for index"""
	def GET(self):
		# return 'Hello world!'
		return render.index(name="roy")

class sinauth:
	"""sina oauth for sinauth"""
	def GET(self):
		return 
		
class sina_callback:
	"""sina oauth callback"""
	def GET(self):
		return 
		
		
if	__name__ == "__main__":
	app.run()
		


