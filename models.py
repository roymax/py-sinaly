import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

engine = create_engine('mysql+mysqldb://root:@localhost:3306/SINALY?charset=utf8&use_unicode=0', pool_recycle=3600)

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class User(Base):
	__tablename__ = 'users'
	__table_args__ = {'mysql_engine':'InnoDB'}

	id = Column(BIGINT, primary_key=True)
	passport = Column(String(32)) 
	nickname = Column(String(32))
	password = Column(String(32))
	provider = Column(String(4))
	token = Column(String(32))
	secret = Column(String(32))
	trunk_key = Column(String(42))
	
	def __init__(self, passport, nickname, password, provider, token, secret, trunk_key ):
		self.passport = passport
		self.nickname = nickname
		self.password = password
		self.provider = provider
		self.token = token
		self.secret = secret
		self.trunk_key = trunk_key
	
	def __repr__(self)   :
		return "<User('%s','%s')>" % (self.passport, self.password)
users_table = User.__table__    

class Session(Base):
	__tablename__ = 'sessions'
	__table_args__ = {'mysql_engine':'InnoDB'}
	
	session_id  = Column(CHAR(128),unique=True, primary_key=True) 
	atime = Column(TIMESTAMP, default=datetime.datetime.now)
	data = Column(TEXT)
	
	def __init__(self, session_id, atime, data ):
		self.session_id = session_id
		self.atime = atime
		self.data = data
	    
	def __repr__(self):
		return "Session('%s', '%s','%s')" % (self.session_id , self.atime, self.data)
	
sessions_table = Session.__table__   

metadata = Base.metadata

if __name__ == "__main__":
	metadata.create_all(engine)