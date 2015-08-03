#include "cpu.h"
#include "internals.h"
#include "disas/disas.h"
#include "tcg-op.h"
#include "qemu/log.h"
#include "qemu/bitops.h"
#include "arm_ldst.h"

#include "exec/helper-proto.h"

#include "back-annotation/my_defines.h"
#include "back-annotation/operations.h"

uint32_t Cumulative_latency = 0;
TBInfo TB_record[MAX_TB] = {{{{0}}}}; // Need bound checking on this
uint32_t tb_IDtracker = 0;      // tracks path of execution through ID
target_ulong tb_pctracker = 0;  // tracks path of execution
target_ulong pred_pctracker = 0; // tracks predecessor in path of execution
target_ulong gfather_pctracker = 0; // tracks predecessor's predecessor in path of execution
/* TB metric storage array. For each TB, holds metrics per predecessor */

void HELPER(increment_latency)(uint64_t tbCount, uint64_t startPC)
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

inline void gen_op_fc_call_2p (tcg_target_long fc, target_ulong tbCount, target_ulong startPC)
{
    //TCGv_ptr    func;
    TCGArg      args[2];

    //func = tcg_const_ptr(fc);

    args[0] = (TCGArg) tcg_const_i64 (tbCount);
    args[1] = (TCGArg) tcg_const_i64 (startPC);
    //args[0] = (TCGArg) tbCount;
    //args[1] = (TCGArg) startPC;

    //tcg_gen_callN (&tcg_ctx, fc, dh_retvar_void, 2, args);
    tcg_gen_callN (&tcg_ctx, (void *)fc, dh_retvar_void, 2, args);

    tcg_temp_free_i64 ((TCGv_i64)args[0]);
    tcg_temp_free_i64 ((TCGv_i64)args[1]);
    //tcg_temp_free_ptr (func);
}

inline void gen_op_increment_latency(uint32_t tbCount, target_ulong startPC)
{
    gen_op_fc_call_2p ((tcg_target_long) helper_increment_latency, tbCount, startPC);
}
