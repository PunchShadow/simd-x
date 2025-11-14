exe=bfs_high_diameter.bin

ldflags	= -I../../../lib/ -I. -I../../../cpu_alg/

commflags= --compiler-options -Wall -Xptxas -v -Xcudafe -\# --resource-usage 
#commflags+=--generate-line-info --source-in-ptx 
#commflags+=-dryrun
#commflags+=-keep -keep-dir ptx
#commflags+=-maxrregcount=64
cucc= "$(shell which nvcc)"
cc= "$(shell which gcc)"
# Allow overriding the target architecture: `make CUDA_ARCH=sm_90`.
CUDA_ARCH ?= sm_86
CUDA_VARCH ?= compute_86
CUGENCODE ?= -gencode arch=$(CUDA_VARCH),code=$(CUDA_ARCH) \
			 -gencode arch=$(CUDA_VARCH),code=$(CUDA_VARCH)
cuflags= $(CUGENCODE)  $(commflags) #-Xptxas -dlcm=cg#disable l1 cache
cuflags+=-D__VOTE__

ifeq ($(monitor), 1)
	cuflags+= -DENABLE_MONITORING
endif

ifeq ($(check), 1)
	cuflags+= -DENABLE_CHECKING
endif

ifeq ($(debug), 1)
	cuflags+= -G -g -O0
	cflags += -g -O0
else
	cflags += -O3
	cuflags+= -O3
endif


#cuflags+= -ccbin=g++ -Xcompiler -fopenmp

objs	= $(patsubst %.cu,%.o,$(wildcard *.cu))

deps	= $(wildcard ../../../lib/*.h) \
		  $(wildcard ../../../lib/*.cuh) \
		  $(wildcard ../../../lib/*.hpp) \
		  $(wildcard ./*.h) \
		  $(wildcard ../../../cpu_alg/*.hpp) \
		  Makefile

%.o:%.cu $(deps)
	$(cucc) -c $(cuflags) $(ldflags) $< -o $@

$(exe):$(objs)
	$(cucc) $(objs) $(cuflags) $(ldflags) -o $(exe)

test:$(exe)
	./bfs /mnt/raid0_huge/hang/roadNet-CA/roadNet-CA.mtx_beg_pos.bin /mnt/raid0_huge/hang/roadNet-CA/roadNet-CA.mtx_csr.bin
clean:
	rm -rf *.o generator/*.o ${exe}
