from fabric.api import sudo, cd, put

REDIS_TAR='http://download.redis.io/redis-stable.tar.gz'

#TODO read paths and ports from redis config file

def install_redis():

	sudo('useradd redis', pty=True)
	sudo('mkdir /etc/redis', pty=True)

	sudo('mkdir /var/redis', pty=True)
	sudo('mkdir /var/redis/6379', pty=True)
	sudo('chown redis:redis /var/redis/6379', pty=True)
	sudo('chown redis:redis /var/redis', pty=True)

	sudo('touch /var/log/redis_6379.log', pty=True)
	sudo('chmod 0777 /var/log/redis_6379.log', pty=True)
	put('redis/redis.conf', '/etc/redis/6379.conf', use_sudo=True)

	put('redis/redis.init', '/etc/rc.d/init.d/redis_6379', use_sudo=True, mode=751)
	sudo('chkconfig --add redis_6379', pty=True)

	sudo('wget %s' % REDIS_TAR, pty=True)
	sudo('tar xvzf redis-stable.tar.gz', pty=True)
	with cd('redis-stable'):
		sudo('make', pty=True)
		sudo('make install', pty=True)
		sudo('cp src/redis-server /usr/local/bin/')
		sudo('cp src/redis-cli /usr/local/bin/')

	sudo('service redis_6379 start', pty=True)

