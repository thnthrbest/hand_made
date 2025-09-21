Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """D:\GitHub\hand_made\python_handmade\sever\start_main.bat""", 7, False
' Docs https://www.vbsedit.com/html/6f28899c-d653-4555-8a59-49640b0e32ea.asp
' intWindowStyle	Description

' 0 Hides the window and activates another window.

' 1 Activates and displays a window. If the window is minimized or maximized, the system restores it to its original size and position. An application should specify this flag when displaying the window for the first time.

' 2 Activates the window and displays it as a minimized window.

' 3 Activates the window and displays it as a maximized window.

' 4 Displays a window in its most recent size and position. The active window remains active.

' 5 Activates the window and displays it in its current size and position.

' 6 Minimizes the specified window and activates the next top-level window in the Z order.

' 7 Displays the window as a minimized window. The active window remains active.

' 8 Displays the window in its current state. The active window remains active.

' 9 Activates and displays the window. If the window is minimized or maximized, the system restores it to its original size and position. An application should specify this flag when restoring a minimized window.

' 10 Sets the show-state based on the state of the program that started the application.
