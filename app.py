#!/usr/bin/env python
# encoding: utf-8
import sys, os
abspath = os.path.dirname(__file__)
sys.path.append(abspath)
os.chdir(abspath)

import web 
from web.contrib.template import render_jinja
from sinat import Sinat, OAuthToken, OAuthConsumer  
from trunkly import Trunkly 


reload(sys) 
sys.setdefaultencoding("utf-8")

web.config.debug = False

urls = (
	"/" , "Index",
	"/sina/auth", "Sinauth",
	"/sina/auth/callback", "SinaCallback", 
	"/trunk", "Trunk",
	"/trunk/unbind", "TrunkUnbind",
	"/home", "Home",
	"/logout", "Logout",
	"/faq", "Faq",
	"/about", "About",
	"/changelog","Changelog",
) 
app = web.application(urls,globals())
application = app.wsgifunc()

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

#db = web.database(dbn='mysql', db='roymax_sinaly', user='roymax_sinaly', pw='654no8BAxf8hqnT')
db = web.database(dbn='mysql', db='SINALY', user='root', pw='')
store = web.session.DBStore(db, 'sessions')
#store = web.session.DiskStore(os.path.join(abspath,'sessions'))
session = web.session.Session(app, store, initializer={'count': 0})

web.config.session_parameters['secret_key']='Kdskjfka@#fWERTYUINSBC$%^^&*()'

#jinja2
render = render_jinja(
        os.path.join(abspath,'views') ,   # Set template directory.
        encoding = 'utf-8',                         # Encoding.
    )  

class Index:
	"""docstring for index"""
	def GET(self):
		if session.get('logged',False):
			user = db.select('users',dict(passport=session.uid, provider=session.provider), 
					where='passport = $passport and provider = $provider ')
			key = user[0]['trunk_key']
			if not key: 
				web.seeother("/trunk")
			else:                 
				
				session.trunk_key=key
				web.seeother("/home")  
		
		return render.index()

class Home:
	def GET(self):
		if not session.get('logged' ,False):
			 web.seeother("/") 
		
		return render.home(nickname=session.nickname)

class Logout:
	def GET(self):
		session.kill() 

		return render.index()

class Trunk:
	def GET(self):
		if not session.get('logged' ,False):
			 web.seeother("/")
			
		return render.trunk()
		
	def POST(self):
		if not session.get('logged' ,False):
			web.seeother("/")
		data = web.input()
		username = data.username
		password = data.password
		
		logger.debug('username %s ' % username)
		if username and password:
			try:
				logger.debug('request api_key ')
				t = Trunkly()
				apikey = t.get_api_key(username=username,password=password)
				logger.debug('api_key is %s' % apikey)
				db.update('users',vars=dict(passport=session.uid, provider=session.provider), where='passport = $passport and provider = $provider ',trunk_key=apikey['api_key'])
				
 				session.trunk_key = apikey['api_key']
			except:
				logger.debug("%s" % Exception)
				return render.trunk(username=username , error="Trunk.ly认证失败.")      
			
		web.seeother("/home")
		
class TrunkUnbind:
	def POST(self):
		if not session.get('logged' ,False):
			web.seeother("/")
		try:
			db.update('users',vars=dict(passport=session.uid, provider=session.provider), where='passport = $passport and provider = $provider ',trunk_key=None)
		except:
			pass
			 
		web.seeother("/trunk")

class Faq:
	def GET(self):
		return render.faq()

class Changelog:                 
	def GET(self):
		return render.changelog()

class About:
	def GET(self):
		return render.about()
		
		
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
		session.logged=True
		session.nickname=data['screen_name']
		session.uid=data['id']
		session.provider='sina'
		
		web.seeother("/") 
		
		
if	__name__ == "__main__":
	app.run()
		


