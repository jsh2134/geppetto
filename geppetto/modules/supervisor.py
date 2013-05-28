from fabric.api import sudo, put

#TODO virtualenv, fuck?!

def install_supervisor():
	# Install Supervisor Config
	sudo('mkdir %s/etc/' % venv)
	sudo('mkdir /var/log/supervisord/')
	
	# TODO who should actually chown?
	sudo('chown kickbacker:kickbacker /var/log/supervisord')

	put('supervisord.conf', '%s/etc/supervisord.conf' % venv, use_sudo=True)
	put('supervisord.init', '/etc/rc.d/init.d/supervisord', use_sudo=True)
	sudo('chkconfig --add supervisord')
	sudo('chmod +x /etc/init.d/supervisord')
