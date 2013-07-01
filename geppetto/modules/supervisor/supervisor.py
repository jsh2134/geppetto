import os

from fabric.api import sudo, put

def install_supervisor():

	supervisor_home = os.path.join(os.sep, 'etc')
	supervisor_log = os.path.join(os.sep, 'var', 'log', 'supervisord')
	service_name = 'supervisord'
	supervisor_init = os.path.join(os.sep, 'etc','rc.d','init.d',service_name)

	# Install Supervisor Config
	sudo('mkdir -p %s' % supervisor_home)
	sudo('mkdir -p %s' % supervisor_log)
	
	sudo('useradd supervisor', pty=True)
	sudo('chown supervisor:supervisor %s' % (supervisor_log))

	put('supervisord.conf', '%s' % supervisor_home, use_sudo=True)
	put('supervisord.init', supervisor_init, use_sudo=True)
	sudo('chkconfig --add %s' % service_name)
	sudo('chmod +x %s' % os.path.join(os.sep, 'etc', 'init.d', service_name) )
