CFLAGS = -g -O9 -fPIC -Wall -pedantic 	# for Linux and other gcc systems
OP=$(CFLAGS)  
CC=gcc	#for Linux

# compilation rule for general cases
.o :
	$(CC) $(OP) -o $@ $? -lm
.c.o:
	$(CC) -c $(OP) $<     

SWEOBJ = swedate.o swehouse.o swejpl.o swemmoon.o swemplan.o swepcalc.o sweph.o\
	swepdate.o swephlib.o swecl.o 

swetest: swetest.o libswe.a
	$(CC) $(OP) -o swetest swetest.o -L. -lswe -lm


swemini: swemini.o libswe.a
	$(CC) $(OP) -o swemini swemini.o -L. -lswe -lm

# create an archive and a dynamic link libary fro SwissEph
# a user of this library will inlcude swephexp.h  and link with -lswe

libswe.a: $(SWEOBJ)
	ar r libswe.a	$(SWEOBJ)

libswe.sl: $(SWEOBJ)
	ld -b -o libswe.sl	$(SWEOBJ)

clean:
	rm -f *.o swetest libswe*
	
###
swecl.o: swejpl.h sweodef.h swephexp.h swedll.h sweph.h swephlib.h
swedate.o: swephexp.h sweodef.h swedll.h
swehouse.o: swephexp.h sweodef.h swedll.h swephlib.h swehouse.h
swejpl.o: swephexp.h sweodef.h swedll.h sweph.h swejpl.h
swemmoon.o: swephexp.h sweodef.h swedll.h sweph.h swephlib.h
swemplan.o: swephexp.h sweodef.h swedll.h sweph.h swephlib.h swemptab.c
swepcalc.o: swepcalc.h sweodef.h swephexp.h swedll.h
sweph.o: swejpl.h sweodef.h swephexp.h swedll.h sweph.h swephlib.h
swephlib.o: swephexp.h sweodef.h swedll.h sweph.h swephlib.h
swetest.o: sweodef.h swephexp.h swedll.h
