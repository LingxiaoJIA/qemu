#ifndef _MY_DEFINES_H_
#define _MY_DEFINES_H_

#define MAX_INSTTS_PER_TB 100
#define MAX_TB 10000
#define MAX_PRED 10

typedef struct TBInfo TBInfo;
extern unsigned long Cumulative_latency;
extern TBInfo TB_record[];
extern target_ulong tb_pctracker;
extern uint32_t tb_IDtracker; //tracks path of execution through ID
extern void cz_unseenPair(uint32_t tbID);

//data struct to store per TB metrics for a given
//predecesssor
typedef struct TBCz {
  uint32_t predID;//predecessor ID
  uint32_t latency;
  //uint32_t energy;
} TBCz;

struct TBInfo {
  //stores tb metrics for each predecessor encountered
  TBCz tbMetrics[MAX_PRED];
  //count of predecessors encountered
  uint32_t predCount;
};

#endif

