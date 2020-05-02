import curses
import time

screen = curses.initscr()
screen.clear()

curses.start_color()
curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
last_line = "last line"
y = int(screen.getmaxyx()[0])
x = int(screen.getmaxyx()[1])
screen.addstr(y-1, 0, last_line, curses.color_pair(1))
screen.refresh()
k = screen.getch()

time.sleep(10)