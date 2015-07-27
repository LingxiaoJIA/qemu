#ifndef _MY_DEFINES_H_
#define _MY_DEFINES_H_

#define MAX_INSTTS_PER_TB 100
#define MAX_TB 10000
#define MAX_PRED 10

extern uint32_t Cumulative_latency;
extern uint32_t tb_IDtracker; //tracks path of execution through ID
extern target_ulong tb_pctracker;
extern void cz_unseenPair(uint32_t tbID);

//data struct to store per TB metrics for a given
//predecesssor
typedef struct TBCz {
  uint32_t predID;//predecessor ID
  uint32_t latency;
  //uint32_t energy;
} TBCz;

typedef struct TBInfo {
  //stores tb metrics for each predecessor encountered
  TBCz tbMetrics[MAX_PRED];
  //count of predecessors encountered
  uint32_t predCount;
} TBInfo;

extern TBInfo TB_record[MAX_TB];
#endif

