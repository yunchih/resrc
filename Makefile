

install:
	python setup.py install

build:
	python setup.py install

package-arch:
	makepkg

package-github:
	./make-src-pkg.sh

clean:
	rm -fr pkg dist build
