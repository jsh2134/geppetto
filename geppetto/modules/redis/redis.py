from fabric.api import sudo, cd, put
import os

REDIS_TAR = 'http://download.redis.io/redis-stable.tar.gz'
REDIS_FILES = os.path.join(os.getcwd(),'modules','redis')

def install_redis(config):

	port = config['port']
	redis_etc = os.path.join(os.sep, 'etc','redis')
	redis_conf = os.path.join(redis_etc,'%s.conf' % port)
	redis_init = 'redis_%s' % port
	redis_init_full_path = os.path.join(os.sep, 'etc','rc.d','init.d',redis_init)
	redis_home = os.path.join(os.sep, 'var','redis', port)
	redis_log = os.path.join(os.sep, 'var','log', 'redis_%s.log' % port)

	sudo('useradd redis', pty=True)
	sudo('mkdir -p %s' % redis_etc, pty=True)
	sudo('mkdir -p %s' % redis_home, pty=True)
	sudo('chown redis:redis %s' % redis_home, pty=True)
	sudo('touch %s' % redis_log, pty=True)
	sudo('chmod 777 %s' % redis_log, pty=True)
	put(os.path.join(REDIS_FILES, 'redis.conf'), redis_conf, use_sudo=True)

	put(os.path.join(REDIS_FILES,'redis.init'), redis_init_full_path, use_sudo=True, mode=751)
	sudo('chkconfig --add %s' % redis_init, pty=True)

	sudo('wget %s' % REDIS_TAR, pty=True)
	sudo('tar xvzf %s' % REDIS_TAR.split('/')[-1:][0], pty=True)
	with cd('redis-stable'):
		sudo('make', pty=True)
		sudo('make install', pty=True)
		sudo('cp src/redis-server /usr/local/bin/')
		sudo('cp src/redis-cli /usr/local/bin/')

	sudo('service %s start' % redis_init, pty=True)

