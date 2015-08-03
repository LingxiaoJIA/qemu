#ifndef _OPERATIONS_
#define _OPERATIONS_

#include "scall_annotations.h"
#include "my_defines.h"


//uint32_t dyn_TBcnt = 0;
target_ulong tb_pctracker = 0; //tracks path of execution
uint32_t tb_IDtracker = 0; //tracks path of execution through ID
target_ulong pred_pctracker = 0; //tracks predecessor in path of execution
target_ulong gfather_pctracker = 0; //tracks predecessor's predecessor 
                                //in path of execution
//TB metric storage array. For each TB, holds metrics per
//predecessor
struct tbInfo TB_record[MAX_TB] = {{{{0}}}}; //Need bound checking on this
uint32_t cumulative_latency = 0;

//void print_tb_encountered(int32_t tb_count, target_ulong startPC)
//{
//
//  printf("TB_ENCOUNTERED is %d, address %x\n", tb_count, startPC);
//  dyn_TBcnt++;
//  printf("Dynamic count of TBs is %u\n", dyn_TBcnt);
//
//}

void increment_latency(uint32_t tb_count, target_ulong startPC)
{
  //increment latency count for this tb
  //cumulative_latency = cumulative_latency + TB_latency[tb_count];
  unsigned int i, predNum;
  //iterate through TB record to find metric for given pred
  predNum = TB_record[tb_count]._predCount;
  for(i=0; i < predNum; i++)
  {
    //if( (TB_record[tb_count]._tbMetrics[i])._predPC == tb_pctracker )
    if( (TB_record[tb_count]._tbMetrics[i])._predID == tb_IDtracker )
    {
      cumulative_latency += (TB_record[tb_count]._tbMetrics[i])._latency;
      break;
    }
  }
  //update predecessor and current tb trackers
  gfather_pctracker = pred_pctracker;
  pred_pctracker = tb_pctracker;
  tb_pctracker = startPC;
  tb_IDtracker = tb_count;
}

//tcg/tcg.h:typedef tcg_target_ulong TCGArg;
//static inline void gen_op_fc_call_1p (tcg_target_long fc, tcg_target_long param)
static inline void gen_op_fc_call_2p (tcg_target_long fc, uint32_t tbCount, target_ulong startPC)
{
    TCGv_ptr            f;
    TCGArg              args[2];
    int                 sizemask = 0;

    f = tcg_const_ptr (fc);
    //args[0] = tcg_const_ptr (param);
    //args[0] = tcg_const_i32 (tbCount);
    args[0] = tcg_const_i64 (tbCount);
    args[1] = tcg_const_ptr (startPC);
    //args[0] = (tcg_const_i32 (param)).i32; //debugging to check if it is struct - 12 Nov Suhas
    dh_sizemask(ptr, 1);
    tcg_gen_callN (&tcg_ctx, f, 0, sizemask, dh_retvar_void, 2, args);

    tcg_temp_free_ptr (args[0]);
    tcg_temp_free_ptr (args[1]);
    tcg_temp_free_ptr (f);
    //printf("TB_ENCOUNTERED1 \n" );
}




////static inline void gen_op_print_tb_encountered (unsigned int n)
//static inline void gen_op_print_tb_encountered (int32_t n, target_ulong startPC)
//{
//    gen_op_fc_call_2p ((tcg_target_long) print_tb_encountered, n, startPC);
//    //printf("TB_ENCOUNTERED2 \n" );
//}

static inline void gen_op_increment_latency(uint32_t n, target_ulong startPC)
{
    gen_op_fc_call_2p ((tcg_target_long) increment_latency, n, startPC);
    //printf("TB_ENCOUNTERED2 \n" );
}

#endif


