import yaml
from sqlalchemy import create_engine

stream = open("db.yaml", 'r')
mysql_config =  yaml.load(stream)
stream.close()
engine = create_engine("mysql://%s:%s@%s/%s" % (mysql_config['username'], mysql_config['password'], mysql_config['host'], mysql_config['database']) )
