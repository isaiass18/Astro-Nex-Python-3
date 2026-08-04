CFLAGS=-O2 -march=i686   -pipe  -fPIC
CC=gcc	

all: pyso

swig: pysw.i
	swig -python pysw.i

pyobj: swig
	$(CC) $(CFLAGS) -c  pysw_wrap.c   -I/usr/include/python2.5 -I/usr/lib/python2.5/config

pyso: pyobj
	$(CC) -shared  pysw_wrap.o   -o  _pysw.so -L. -lswe -lm

clean:
	rm -f *.o *.so *.py *.c
	
