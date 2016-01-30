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

prepare_build_dir: clean
	@echo Prepare build directory
	mkdir build
	tar --transform='s,^\.,mamonsu-$(VERSION),'\
		-czf build/mamonsu-$(VERSION).tar.gz .\
		--exclude=build
	tar xvf build/mamonsu-$(VERSION).tar.gz -C build
	cp build/mamonsu-$(VERSION).tar.gz \
		build/mamonsu-$(VERSION)/rpm/SOURCES
	@echo

deb: prepare_build_dir
	@echo Build deb
	cd build/mamonsu-$(VERSION) && dpkg-buildpackage -b
	cp -av build/mamonsu*.deb .
	@echo

rpm: prepare_build_dir
	@echo Build rpm
	chown -R root.root build/mamonsu-$(VERSION)
	rpmbuild -ba --define '_topdir $(CURDIR)/build/mamonsu-$(VERSION)/rpm'\
		$(CURDIR)/build/mamonsu-$(VERSION)/rpm/SPECS/mamonsu.spec
	cp -av $(CURDIR)/build/mamonsu-$(VERSION)/rpm/RPMS/noarch/mamonsu*.rpm .
	@echo

clean: python_clean
	rm -rf build

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
