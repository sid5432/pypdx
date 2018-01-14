clean:
	rm -f Makefile.bak *~ */*~ *-dump.json pdx.dump

realclean: clean
	rm -rf *.db3 *.json *.pyc */*.pyc */__pycache__ __pycache__ .cache */.cache
	rm -rf build dist pypdx.egg-info
	
build: realclean
	python setup.py build

check:
	python setup.py check --strict --restructuredtext

dist: check build
	python setup.py sdist bdist_wheel

upload: dist
	twine upload dist/*

install: build
	python setup.py install

test: testall

testall:
	echo "run tests in test/"
	pytest

doc:
	pandoc README.md -o README.rst

html: doc
	rst2html5.py README.rst > README.html
		
tag:
	git tag `grep version pypdx/__init__.py | cut -d '"' -f 2` -m "Add a tag so we can put this on PyPI"
	git push --tags origin master
	
