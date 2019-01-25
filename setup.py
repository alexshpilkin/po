import setuptools

with open('README.rst', 'r') as fp:
	for line in fp:
		if not line[:-1]: break
	readme = fp.read()

setuptools.setup(
	name='po',
	version='0.1.0',
	author='Alexander Shpilkin',
	author_email='ashpilkin@gmail.com',
	description='Reader and writer for PO files',
	long_description=readme,
	long_description_content_type='text/x-rst',
	url='https://github.com/alexshpilkin/po',
	py_modules=['po'],
	install_requires=[],
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
)
