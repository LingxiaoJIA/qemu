#ifndef _OPERATIONS_H_
#define _OPERATIONS_H_

extern target_ulong pred_pctracker;
extern target_ulong gfather_pctracker;
inline void gen_op_increment_latency(target_ulong tbCount, target_ulong startPC);

#endif

