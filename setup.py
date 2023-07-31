from setuptools import setup, find_packages


setup(
    name='qol-helpers',
    author='Fletcher F Thompson',
    author_email='fletcherthompsonx@gmail.com.com',
    url="https://github.com/FletcherFT/qol-helpers/",
    version='0.0.5',
    install_requires=['tqdm', 'opencv-contrib-python', 'pillow', 'scikit-learn', 'scikit-image'
    ],
    packages=find_packages()
)
