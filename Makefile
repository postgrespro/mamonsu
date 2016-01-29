VERSION=$(shell python -c 'import mamonsu; print(mamonsu.__version__)')

all:
	@echo Install
	pip install --upgrade --editable .

publish: clean
	@echo Testing wheel build an installation
	@echo "Build $(VERSION)"
	python setup.py register
	python setup.py sdist upload
	@echo

deb: clean
	@echo Build deb
	dpkg-buildpackage -b
	cp -av ../mamonsu*.deb .
	@echo

rpm: clean
	@echo Build rpm
	cp -a rpm rpmbuild
	tar --transform='s,^\.,mamonsu-$(VERSION),' -czf rpm/SOURCES/mamonsu-$(VERSION).tar.gz .
	mv rpm/SOURCES/mamonsu-$(VERSION).tar.gz rpmbuild/SOURCES/mamonsu-$(VERSION).tar.gz
	chown -R root.root rpmbuild
	rpmbuild -ba --define '_topdir $(CURDIR)/rpmbuild' $(CURDIR)/rpmbuild/SPECS/mamonsu.spec
	cp -av $(CURDIR)/rpmbuild/RPMS/noarch/mamonsu*.rpm .
	@echo

clean: deb_clean rpm_clean python_clean

python_clean:
	@echo Cleaning up python fragments
	rm -rf *.egg dist build .coverage
	find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print
	@echo

deb_clean:
	@echo Cleaning up deb fragments
	rm -rf debian/mamonsu
	rm -rf mamonsu.egg-info
	rm -f build-stamp
	rm -f configure-stamp
	rm -f debian/files
	rm -f debian/mamonsu.debhelper.log
	rm -f debian/mamonsu.postinst.debhelper
	rm -f debian/mamonsu.postrm.debhelper
	rm -f debian/mamonsu.prerm.debhelper
	rm -f debian/mamonsu.substvars
	@echo

rpm_clean:
	@echo Cleaning up rpm fragments
	rm -rf rpmbuild
	find . -name 'rpm-tmp.*' -delete -print
	@echo
