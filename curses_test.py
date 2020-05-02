import curses
import time

screen = curses.initscr()
str_ = "last line"
screen.addstr(str(screen.getmaxyx()), str_)
# screen.clear()

time.sleep(3)