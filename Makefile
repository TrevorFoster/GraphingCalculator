SRC = pyglet-1.2alpha1

all: extract build clean

extract:
	cd lib && \
	tar -zxvf $(SRC).tar.gz

build:	
	cd lib/$(SRC) && \
	python setup.py build && \
	cp -R build/lib/pyglet ../pyglet

clean:
	cd lib && rm -rf $(SRC)