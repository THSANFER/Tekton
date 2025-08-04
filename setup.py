# setup.py
from setuptools import setup, find_packages

setup(
    name='sgtek',
    version='1.0.0',
    author='Tiago Henrique e Fernando Candido',
    description='Sistema de Gerenciamento para a Tektõn Presentes',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'sgtek = views.__main__:run_app',
        ],
    },
    python_requires='>=3.9',
    install_requires=[
        'PySide6',
        'Pillow',
        'qrcode',
        'GitPython',
    ],
)
