clean:
	rm -f Makefile.bak *~ lib/*~ test/*~ *-dump.json

realclean: clean
	rm -rf *.db3 *.json *.pyc test/*.pyc test/__pycache__ __pycache__ .cache test/.cache

testall:
	echo "run tests in test/"
	pytest

