from setuptools              import setup
from setuptools.command.test import test as Test

class CustomTest(Test):
	user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

	def initialize_options(self):
		super().initialize_options()
		self.pytest_args = " ".join([
			"-v",
			"--cov",
			"--cov-report term:skip-covered"
			"--cov-report annotate"
		])

	def run_tests(self):
		from shlex  import split
		from sys    import exit
		from pytest import main

		exit(main(split(self.pytest_args)))

with open('README.rst', 'r') as fp:
	for line in fp:
		if not line[:-1]: break
	readme = fp.read()

setup(
	name='po',
	version='0.1.0',
	author='Alexander Shpilkin',
	author_email='ashpilkin@gmail.com',
	description='Reader and writer for PO files',
	long_description=readme,
	long_description_content_type='text/x-rst',
	url='https://github.com/alexshpilkin/po',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: Other Audience',
		'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'Topic :: Software Development :: Localization',
		'Topic :: Text Processing :: Linguistic',
	],

	py_modules=['po'],
	python_requires='~=3.0',
	install_requires=[],
	tests_require=['pytest', 'pytest-cov'],
	cmdclass={
		'test': CustomTest,
	}
)
