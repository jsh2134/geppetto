import os

from fabric.api import env, settings
from fabric.api import sudo, lcd, cd, run, local, put

import ec2

from kickbacker import app
from deploy.amazon_settings import MAIN_IP, aws_defaults

USER_HOME = '/home/jhull/'
REMOTE_DIR = '/home/kickbacker/kb/'
HOME_DIR = app.config['HOME']
TMP_PATH = '/tmp/'
S3CFG_FILE = '.s3cfg'
S3CFG_FP = os.path.join(HOME_DIR, 'deploy', S3CFG_FILE)
KB_BUCKET = 's3://kickbacker/'
HOSTS = {	
			'web1' : { 'user':'ec2-user',
						'host': MAIN_IP,
						'key': os.path.join(USER_HOME, '.ssh',\
								 aws_defaults['keypair']['file']),
						'dir': '/home/kickbacker/kickbacker-env',
						'env': '/home/kickbacker/kickbacker-env/bin/activate',
						'deploy_user': 'kickbacker',
			},
		}





env.key_filename = HOSTS['web1']['key']

def virtualenv(command, use_sudo=True):
	""" Execute a command with sudo under venv """
	with cd(env.directory):
		sudo('source ' + env.activate + ' && ' + command)#, user=env.deploy_user)
		


def host(hostname):
	print "Setting host to %s" % hostname
	env.host_string = "%s@%s" % ( HOSTS[hostname]['user'], \
									HOSTS[hostname]['host'])
	
	# Activate VirtualEnv
	if 'env' in HOSTS[hostname]:
		env.directory = HOSTS[hostname]['dir']
		env.activate = HOSTS[hostname]['env']
		env.deploy_user = HOSTS[hostname]['deploy_user']


def ssh(hostname):
	
	# Set Host
	host(hostname)

	local('ssh -i %s %s@%s' % ( HOSTS[hostname]['key'],
								HOSTS[hostname]['user'],
								HOSTS[hostname]['host'],
								) )


def deploy_web():

	# Create New Instance
	instance = ec2.create_new_instance()

	# Scrub past IP record from known_hosts
	local("ssh-keygen -R %s" % (instance.ip_address) )

	# Set Env Host String
	#env.host_string = "ec2-user@%s" % (instance.ip_address) 
	# In this case web1 is the host
	#TODO make this better
	host('web1')

	# Install Web
	install_web()

	return True


def install_web():

	# Create User
	user = 'kickbacker'
	remote_home_dir = '/home/' + user 
	
	with settings(warn_only=True):
		sudo('useradd -U -m %s' % user)
	
	remote_code_dir = os.path.join(remote_home_dir, 'kb')
	with settings(warn_only=True):
		sudo('mkdir %s' % remote_code_dir)

	# Install packages with yum
	sudo('yum install -y python-devel gcc nginx make')

	# Install python requirements
	put('requirements.txt', remote_home_dir, use_sudo=True)
	virtualenv('pip install -r %s/requirements.txt' % (remote_home_dir))

	# Install s3cmd tools
	#install_s3cmd(remote_home_dir)

	# Install virtualenv 
	sudo('pip install virtualenv')
	venv_name = '%s-env' % user
	venv = os.path.join(remote_home_dir, venv_name)
	sudo('virtualenv --no-site-packages %s' % venv)

	# Activate Virtual Env
	virtualenv('source %s/bin/activate' % venv)
		
	# Install Nginx Config
	put('nginx.conf', '/etc/nginx/nginx.conf', use_sudo=True)


	# Deploy Code
	update_code()

	start_app()

def update_server():
	""" Update code on server """
	update_code()
	restart_app()

def start_app():
	# start nginx
	sudo('service nginx start')

	# start supervisor
	virtualenv('supervisord')


def update_code():
	with lcd(HOME_DIR):
		local('git archive --format=tar.gz --output %s HEAD' % \
									os.path.join(TMP_PATH, 'app.tar.gz'))
	put( os.path.join(TMP_PATH,'app.tar.gz'), os.path.join(REMOTE_DIR, 'app.tar.gz'), use_sudo=True)
	sudo('gunzip -f %s' % os.path.join(REMOTE_DIR, 'app.tar.gz'))
	with cd(REMOTE_DIR):
		with settings(warn_only=True):
			sudo("find . -name '*.pyc' | xargs rm")

		sudo('tar -xvf %s' % os.path.join(REMOTE_DIR, 'app.tar'))


	

