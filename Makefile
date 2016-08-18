VERSION=$(shell python -c 'import mamonsu; print(mamonsu.__version__)')
BUILDDIR=$(CURDIR)/build/mamonsu-$(VERSION)

all:
	@echo Install
	pip install --upgrade --editable .

publish: clean
	@echo "Check rpm version"
	grep ^Version ./rpm/SPECS/mamonsu.spec | grep $(VERSION)
	@echo "Check deb version"
	grep ^mamonsu ./debian/changelog | grep $(VERSION)
	@echo "Python release"
	python setup.py register
	python setup.py sdist upload
	@echo "Git tag"
	git push
	git tag $(VERSION)
	git push --tags
	@echo

prepare_builddir: clean
	@echo Prepare build directory
	mkdir build
	tar --transform='s,^\.,mamonsu-$(VERSION),'\
		-czf build/mamonsu-$(VERSION).tar.gz .\
		--exclude=build
	tar xvf build/mamonsu-$(VERSION).tar.gz -C build
	cp build/mamonsu-$(VERSION).tar.gz \
		$(BUILDDIR)/rpm/SOURCES
	chown -R root.root $(BUILDDIR)
	@echo

deb: prepare_builddir
	@echo Build deb
	cd $(BUILDDIR) && dpkg-buildpackage -b
	cp -av build/mamonsu*.deb .
	@echo

rpm: prepare_builddir
	@echo Build rpm
	rpmbuild -ba --define '_topdir $(BUILDDIR)/rpm'\
		$(BUILDDIR)/rpm/SPECS/mamonsu.spec
	cp -av $(BUILDDIR)/rpm/RPMS/noarch/mamonsu*.rpm .
	@echo

clean: python_clean
	rm -rf build
	rm -f rpm-tmp*
	rm -rf mamonsu.egg-info
	rm -rf *.deb *.rpm

python_clean:
	@echo Cleaning up python fragments
	rm -rf *.egg dist build .coverage
	find . -name '__pycache__' -delete -print -o -name '*.pyc' -delete -print
	@echo

cloud: build/cloud_debian build/cloud_ubuntu build/cloud_centos
	@echo Cloud done

build/cloud_debian: build/cloud_debian_7 build/cloud_debian_8
	@echo Debian done

build/cloud_ubuntu: build/cloud_ubuntu_12_04 build/cloud_ubuntu_14_04 build/cloud_ubuntu_15_10 build/cloud_ubuntu_16_04
	@echo Ubuntu done

build/cloud_centos: build/cloud_centos_6 build/cloud_centos_7
	@echo Centos done

define build_deb
	docker run -v $$(pwd):/var/tmp --rm $1:$2 bash -exc "cd /var/tmp && apt-get update -m && apt-get install -y make dpkg-dev debhelper python-dev python-setuptools && make deb"
endef

define build_rpm
	docker run -v $$(pwd):/var/tmp --rm $1:$2 bash -exc "cd /var/tmp && yum install -y tar make rpm-build python2-devel python-setuptools && make rpm"
endef

define build_and_publish_debian
	rm -f *.deb
	$(call build_deb,debian,$1)
	package_cloud push postgrespro/mamonsu/debian/$2 *.deb
endef

define build_and_publish_ubuntu
	rm -f *.deb
	$(call build_deb,ubuntu,$1)
	package_cloud push postgrespro/mamonsu/ubuntu/$2 *.deb
endef

define build_and_publish_centos
	rm -f *.rpm
	$(call build_rpm,centos,$1)
	package_cloud push postgrespro/mamonsu/el/$1 *.rpm
endef

build/cloud_debian_7:
	$(call build_and_publish_debian,7,wheezy)
	touch build/cloud_debian_7

build/cloud_debian_8:
	$(call build_and_publish_debian,8,jessie)
	touch build/cloud_debian_8

build/cloud_ubuntu_12_04:
	$(call build_and_publish_ubuntu,12.04,precise)
	touch build/cloud_ubuntu_12_04

build/cloud_ubuntu_14_04:
	$(call build_and_publish_ubuntu,14.04,trusty)
	touch build/cloud_ubuntu_14_04

build/cloud_ubuntu_15_10:
	$(call build_and_publish_ubuntu,15.10,wily)
	touch build/cloud_ubuntu_15_10

build/cloud_ubuntu_16_04:
	$(call build_and_publish_ubuntu,16.04,xenial)
	touch build/cloud_ubuntu_16_04

build/cloud_centos_6:
	$(call build_and_publish_centos,6)
	touch build/cloud_centos_6

build/cloud_centos_7:
	$(call build_and_publish_centos,7)
	touch build/cloud_centos_7
