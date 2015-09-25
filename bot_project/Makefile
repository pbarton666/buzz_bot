.PHONY : console start server tags

console:
	exec ./console.py

start: server

server:
	exec ./start-buzzbot.py

tags:
	ctags -R .

clean:
	find . -type f -name "*.pyc" -exec rm {} \;
