#ifndef UTIL_H
#define UTIL_H

#include <stdio.h>
static void HandleError( cudaError_t err,
                         const char *file,
                         int line ) {
    if (err != cudaSuccess) {
        printf( "%s in %s at line %d\n", \
        cudaGetErrorString( err ),
                file, line );
        exit( EXIT_FAILURE );
    }
}
#define H_ERR( err ) \
  (HandleError( err, __FILE__, __LINE__ ))


#define SML_MID 32	
#define MID_LRG 1024	
//#define SWITCH_TO (float)10.3
#define SWITCH_TO (float)0.2
#define SWITCH_BACK (float)0.4
//#define SWITCH_BACK (float)0.3

//#define SML_MID 0	
//#define MID_LRG	6553600

//#define SML_MID 0	
//#define MID_LRG	0
#ifndef GPUID
#define GPUID		0
#endif

#ifndef THDS_NUM
#define THDS_NUM	512
#endif

#ifndef BLKS_NUM
#define BLKS_NUM	512
#endif
//#define BLKS_NUM	96	

#endif
