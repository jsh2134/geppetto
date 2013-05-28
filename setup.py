from setuptools import setup


setup(	name = "geppetto",
		version = "0.1",
		description = "Define, Deploy and Control Amazon Infrastructure fast.",
		author = "Jeff Hull",
		author_email = "jsh2134@gmail.com",
		url = "http://www.github.com/jsh2134/geppetto",
		license = "LICENSE.txt",
		packages = ['geppetto'],
		install_requires = ['boto>=2.4', 'fabric>=1.4']
	)
		
