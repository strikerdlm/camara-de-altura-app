from setuptools import setup, find_packages

setup(
    name="camara-hiperbarica-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "ttkbootstrap>=1.10.1",
        "Pillow>=9.5.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "xlsxwriter>=3.1.0",
        "tkinter-tooltip>=2.1.0",
        "tkinterweb>=3.23.5",
        "tkinter-calendar>=0.4.0",
        "tkinter-tabview>=0.2.1",
        "tkinter-validation>=0.1.0"
    ],
    author="Fuerza Aérea Colombiana",
    author_email="",
    description="Sistema de registro para entrenamiento en cámara hipobárica",
    keywords="camara, hipobárica, entrenamiento, registro",
    python_requires=">=3.8"
)