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

void HELPER(increment_latency)(uint64_t tb_id, uint64_t startPC)
{
    unsigned int i, predNum;
    TBInfo *tb_info = &TB_record[tb_id];
    predNum = tb_info -> predCount;

    /* increment latency count for this tb */
    /* iterate through TB record to find metric for given pred */
    for (i = 0; i < predNum; ++i) {
        if ((tb_info -> tbMetrics[i]).predID == tb_IDtracker) {
            Cumulative_latency += (tb_info -> tbMetrics[i]).latency;
            break;
        }
    }
    //update predecessor and current tb trackers
    gfather_pctracker = pred_pctracker;
    pred_pctracker = tb_pctracker;
    tb_pctracker = startPC;
    tb_IDtracker = tb_id;
}

inline void gen_op_fc_call_2p (tcg_target_long fc, target_ulong tb_id, target_ulong startPC)
{
    //TCGv_ptr    func;
    TCGArg      args[2];

    //func = tcg_const_ptr(fc);

    args[0] = (TCGArg) tcg_const_i64 (tb_id);
    args[1] = (TCGArg) tcg_const_i64 (startPC);
    //args[0] = (TCGArg) tb_id;
    //args[1] = (TCGArg) startPC;

    //tcg_gen_callN (&tcg_ctx, fc, dh_retvar_void, 2, args);
    tcg_gen_callN (&tcg_ctx, (void *)fc, dh_retvar_void, 2, args);

    tcg_temp_free_i64 ((TCGv_i64)args[0]);
    tcg_temp_free_i64 ((TCGv_i64)args[1]);
    //tcg_temp_free_ptr (func);
}

inline void gen_op_increment_latency(uint32_t tb_id, target_ulong startPC)
{
    gen_op_fc_call_2p ((tcg_target_long) helper_increment_latency, tb_id, startPC);
}
