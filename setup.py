from setuptools import setup, find_packages

setup(
    name='bing-wallpaper-downloader',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A background application that downloads Bing wallpapers based on user-defined settings.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',
        'Pillow',
        'schedule',
    ],
    entry_points={
        'console_scripts': [
            'bing-wallpaper-downloader=main:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)