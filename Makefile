VERSION=$(shell python -c 'import mamonsu; print(mamonsu.__version__)')
BUILDDIR=$(CURDIR)/build/mamonsu-$(VERSION)

all:
	pip install --upgrade --editable .

publish: clean test
	grep ^Version ./packaging/rpm/SPECS/mamonsu.spec | grep $(VERSION)
	grep ^mamonsu ./packaging/debian/changelog | grep $(VERSION)
	python setup.py register
	python setup.py sdist upload
	git push
	git tag $(VERSION)
	git push --tags

clean: python_clean
	rm -rf build
	rm -f rpm-tmp*
	rm -rf mamonsu.egg-info
	rm -rf *.deb *.rpm yum-root-*

python_clean:
	rm -rf *.egg dist build .coverage
	find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print

include Makefile.pkg
include Makefile.tests
