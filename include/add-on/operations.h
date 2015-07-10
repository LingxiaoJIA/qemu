#ifndef _OPERATIONS_H_
#define _OPERATIONS_H_

#include "my_defines.h"

uint32_t Cumulative_latency = 0;
TBInfo TB_record[MAX_TB] = {{{{0}}}}; // Need bound checking on this
target_ulong tb_pctracker = 0;  // tracks path of execution
uint32_t tb_IDtracker = 0;      // tracks path of execution through ID
target_ulong pred_pctracker = 0; // tracks predecessor in path of execution
target_ulong gfather_pctracker = 0; // tracks predecessor's predecessor in path of execution
/* TB metric storage array. For each TB, holds metrics per predecessor */

void increment_latency(uint32_t tbCount, target_ulong startPC)
{
    /* increment latency count for this tb */
    unsigned int i, predNum;
    /* iterate through TB record to find metric for given pred */
    predNum = TB_record[tbCount].predCount;

    for (i = 0; i < predNum; ++i) {
        if ((TB_record[tbCount].tbMetrics[i]).predID == tb_IDtracker) {
            Cumulative_latency += (TB_record[tbCount].tbMetrics[i]).latency;
            break;
        }
    }
    //update predecessor and current tb trackers
    gfather_pctracker = pred_pctracker;
    pred_pctracker = tb_pctracker;
    tb_pctracker = startPC;
    tb_IDtracker = tbCount;
}

//tcg/tcg.h:typedef tcg_target_ulong TCGArg;
static inline void gen_op_fc_call_2p (tcg_target_long fc, uint32_t tbCount, target_ulong startPC)
{
    TCGv_ptr    func;
    TCGArg      args[2];

    func = tcg_const_ptr(fc);

    args[0] = tcg_const_i64 (tbCount);
    args[1] = tcg_const_ptr (startPC);

    tcg_gen_callN (&tcg_ctx, func, dh_retvar_void, 2, args);

    tcg_temp_free_ptr (args[0]);
    tcg_temp_free_ptr (args[1]);
    tcg_temp_free_ptr (func);
    //printf("TB_ENCOUNTERED1 \n" );
}

static inline void gen_op_increment_latency(uint32_t tbCount, target_ulong startPC)
{
    gen_op_fc_call_2p ((tcg_target_long) increment_latency, tbCount, startPC);
    //printf("TB_ENCOUNTERED2 \n" );
}

#endif

