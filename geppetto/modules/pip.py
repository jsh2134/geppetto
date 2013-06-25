from fabric.api import sudo, run

def is_pip_installed():
	#TODO
	return False

def install_pip():
	sudo('curl -O http://pypi.python.org/packages/source/p/pip/pip-1.0.tar.gz')
	run('tar xvfz pip-1.0.tar.gz')
	sudo('cd pip-1.0 && python setup.py install')
