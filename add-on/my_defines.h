#ifndef __MY_DEFINES_H
#define __MY_DEFINES_H

#define MAX_INSTTS_PER_TB 100
#define MAX_TB 10000
#define MAX_PRED 10

//data struct to store per TB metrics for a given
//predecesssor
struct tbCz
{
  //target_ulong _predPC;
  uint32_t _predID;//predecessor ID
  uint32_t _latency;
  //uint32_t _energy;
};

struct tbInfo
{
  //stores tb metrics for each predecessor encountered
  struct tbCz _tbMetrics[MAX_PRED];
  //count of predecessors encountered
  uint32_t _predCount;
};

#endif

