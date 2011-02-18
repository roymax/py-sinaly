import web
from web.contrib.template import render_jinja
from sinat import Sinat, OAuthToken, OAuthConsumer 
import sys

web.config.debug = False

urls = (
	"/" , "Index",
	"/sina/auth", "Sinauth",
	"/sina/auth/callback", "SinaCallback"
) 
app = web.application(urls,globals()) 

def initlog():
	"""docstring for initlog"""
	import logging
	logger = logging.getLogger("sinaly")
	hd = logging.StreamHandler(sys.stdout)
	fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hd.setFormatter(fmt)
	logger.addHandler(hd)
	logger.setLevel(logging.DEBUG)
	return logger
	
logger=initlog()

SINA_CONSUMER_KEY = '3892402622' # your App Key
SINA_CONSUMER_SECRET = '6af8bdaa10fb55fa82089a8a29787f81' # your App Secret  

sinaConsumer = OAuthConsumer(SINA_CONSUMER_KEY, SINA_CONSUMER_SECRET)
########################  
# from sqlalchemy.orm import scoped_session, sessionmaker   
# from models import *   
# def load_sqla(handler):
#     web.ctx.orm = scoped_session(sessionmaker(bind=engine))
#     try:
#         return handler()
#     except web.HTTPError:
#        web.ctx.orm.commit()
#        raise
#     except:
#         web.ctx.orm.rollback()
#         raise
#     finally:
#         web.ctx.orm.commit()
#         # If the above alone doesn't work, uncomment 
#         # the following line:
#         #web.ctx.orm.expunge_all()  
# app.add_processor(load_sqla) 
###########################

db = web.database(dbn='mysql', db='SINALY', user='root', pw='')
store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store, initializer={'count': 0})

#jinja2
render = render_jinja(
        'views',   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
    )  

class Index:
	"""docstring for index"""
	def GET(self):
		# return 'Hello world!'
		access_key=session.get('access_key',None)
		access_secret=session.get('access_secret',None)
	    
		if access_key:
			access_token = OAuthToken(access_key, access_secret) 
			sinat = Sinat(sinaConsumer, access_token=access_token)
			statuses = sinat.statuses__friends_timeline('GET', {'count': 10})
			return render.index(name="roy", statuses=statuses)
		
		return render.index(name="roy")

class Sinauth:
	"""sina oauth for sinauth"""
	def GET(self):                    
		sinat = Sinat(sinaConsumer)
		SINA_CALLBACK = web.ctx.get('homedomain') + '/sina/auth/callback'  #callback url 
		request_token = sinat.get_request_token(SINA_CALLBACK)
		logger.debug('request token: %s' % request_token.key)
		logger.debug('request token secret: %s' % request_token.secret)
		logger.debug('authorization url: %s' % sinat.get_authorization_url(request_token))
		#save token & secret to session
		session.request_token = request_token.key
		session.request_token_secret = request_token.secret       

	   	web.seeother(sinat.get_authorization_url(request_token)) 
		
class SinaCallback:
	"""sina oauth callback"""
	def GET(self):
		logger.debug('callback --------------')
		verifier = web.input().get('oauth_verifier',None) 
		logger.debug('verifier : %s' % verifier)
		sinat = Sinat(sinaConsumer)     
		logger.debug('request token: %s' % session.request_token)
		logger.debug('request token secret: %s' % session.request_token_secret)
		
		request_token = OAuthToken(session.request_token, session.request_token_secret )
		request_token.set_verifier(verifier)
		access_token = sinat.get_access_token(request_token)
		
		logger.debug('access token: %s' % access_token.key)
		logger.debug('access token secret: %s' % access_token.secret)
		
		sinat = Sinat(sinaConsumer, access_token=access_token)
		data = sinat.account__verify_credentials()
		logger.debug('screen name: %s' % data['screen_name'])
		
		uid =  data['id']
		user = db.select('users',dict(passport=uid), where='passport = $passport and provider = "sina"')
		if not user:
			db.insert('users', passport=data['id'],nickname=data['screen_name'], provider="sina", token=access_token.key, secret=access_token.secret)
		else: 
			db.update('users',vars=dict(passport=uid),  where='passport = $passport and provider = \'sina\'', token=access_token.key, secret=access_token.secret ) 
		
		del session.request_token
		del session.request_token_secret
		session.access_key=access_token.key
		session.access_secret=access_token.secret
		
		web.seeother("/") 
		
		
if	__name__ == "__main__":
	app.run()
		


