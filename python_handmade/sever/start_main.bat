@echo off
call "D:\GitHub\hand_made\python_handmade\env\Scripts\activate.bat"
python D:\GitHub\hand_made\python_handmade\test.py
echo Close in 10 Seconds
TIMEOUT /T 10 /NOBREAK
exit