PREFIX ?= /usr/local
PYTHON=python3

build: build-doc build-py

install: install-doc install-py

clean: clean-doc clean-py
	find src/py3/ -type d -name '__pycache__' -exec rm -r {} +

build-doc:
	make -C doc/ html

install-doc: build-doc
	mkdir -pv $(DESTDIR)/$(PREFIX)/share/doc/pywheel/
	cp -rv doc/_build/html $(DESTDIR)/$(PREFIX)/share/doc/pywheel/

clean-doc:
	make -C doc/ clean

build-py:
	$(PYTHON) ./setup.py build

install-py: build-py
	$(PYTHON) ./setup.py install --prefix $(DESTDIR)/$(PREFIX)
	
clean-py:
	$(PYTHON) ./setup.py clean
	rm -rvf build/
	rm -rvf dist/

