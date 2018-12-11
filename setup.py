from distutils.core import setup

topic = """
Development Status :: 1 - Planning
Environment :: Console
Intended Audience :: Other Audience
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Text Processing :: General
"""

setup(
    name='pydodo',
    packages=['pydodo'],
    version='0.0.1',
    description='Markov chain generator',
    author='Oivvio Polite',
    author_email='oivvio@liberationtech.net',
    topic=topic,
)
