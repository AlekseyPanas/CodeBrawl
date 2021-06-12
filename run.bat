@echo off
pip3 > nul
if %ERRORLEVEL%==9009 (
	echo Running python
	pip install pygame
	python run.py
) else (
	echo Running python3
	pip3 install pygame
	python3 run.py
)
pause