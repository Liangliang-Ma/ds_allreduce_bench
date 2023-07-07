import torch
import deepspeed
import deepspeed.comm as dist
import time

deepspeed.init_distributed()

def test_allreduce(reuse_buffer, use_dtype, loop_count):
    b = torch.ones(1024, 1024, dtype=torch.bfloat16).xpu()
    if reuse_buffer:
        a = torch.ones(1024, 1024, dtype=torch.bfloat16).xpu()
        c = torch.ones(1024, 1024, dtype=torch.bfloat16).xpu()
        t = torch.ones(1024, 5, dtype=use_dtype).xpu()
    t_total = 0.0
    start = time.time()
    for i in range(loop_count):
        if not reuse_buffer:
            a = torch.ones(1024, 1024, dtype=torch.bfloat16).xpu()
            c = torch.ones(1024, 1024, dtype=torch.bfloat16).xpu()
            t = torch.ones(1024, 5, dtype=use_dtype).xpu()
        torch.matmul(a, b, out=c)
        torch.matmul(a, b, out=c)
        #v = 0.0000001
        #for i in range(100000):
        #    v = v + 0.01
        dist.barrier(t)
        # print ('barrier end\n', flush=True)
        # # break
        t0 = time.time()
        #dist.all_reduce_low_latency(t)
        dist.all_reduce(t)
        # print ('all_reduce end\n', flush=True)
        t1 = time.time()
        if (i==0 and dist.get_rank()==0):
            print (t.cpu())
        t_total += t1-t0
    end = time.time()
    #print (f'total elapsed {end-start}')
    return t_total

# loop_count = 17920
loop_count = 200
t = test_allreduce(True, torch.bfloat16, loop_count)

if dist.get_rank() == 0:
    print (f'duration = {t}s')
    print (f'avg duration = {t/(loop_count/1000.0)}ms')

#dist.log_summary(show_straggler=True)
