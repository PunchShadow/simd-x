#ifndef HEADER_H
#define HEADER_H
typedef int index_t;
typedef unsigned int vertex_t;
typedef int feature_t;
typedef int weight_t;
typedef unsigned char bit_t;

#define INFTY			(int)-1
#ifndef BLKS_NUM
#define BLKS_NUM		256
#else
#undef BLKS_NUM
#define BLKS_NUM		256
#endif

#define BIN_SZ			8192	
//#define BIN_SZ			32
#endif
