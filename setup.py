from setuptools import setup
import fqueue
import re

setup(
    name = "fqueue",
    version = fqueue.__version__,
    author = re.sub(r'\s+<.*', r'', fqueue.__author__),
    author_email = re.sub(r'(^.*<)|(>.*$)', r'', fqueue.__author__),
    url = fqueue.__url__,
    description = ("Plain file based queue service"),
    long_description = file('README').read(),
    keywords = "queue",
    py_modules = [
        'fqueue',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

