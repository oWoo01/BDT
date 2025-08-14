========================================
         文件夹结构说明
========================================

input/                  # 存放最初的、xtal+atomsk生成的 .lmp 文件

{potential}/            # 势函数名称文件夹
    dump/               # in.crack1-aniso-rlx 输出文件
        {crack system}/
            {Temp}/
                W_{crack system}_{Temp}_{step}_eq.data

    log/                # 各类日志文件
        {crack system}-{Temp}-log          # LAMMPS log 文件
        {crack system}-{Temp}-record       # step-K 对照文件
        {crack system}-{Temp}-outlog       # submit.sh 的 log 文件
        [proc]-{crack system}-{Temp}      # process.py 输出的 step-K-crack length 对照文件

    config/             # in.crack1-aniso-ini 输出文件
        dynamic/        # 动态配置文件
        static/         # 静态配置文件

    pic/                # 绘图存放文件夹
    Kc.txt              # process.py 输出的 crack system-Kc-event type 等文件


========================================
         脚本和工具说明
========================================

apq.py                 # 计算 C/S tensor 和各向异性裂尖位移场需要的常数 a/p/q

batch-run.sh           # 设置势函数、K 和 dK
    ├─ submit.sh       # 提交任务
    │   ├─ displace_dump.data     # 为边界层原子设置位移以施加 K
    │   ├─ in.crack1-aniso-ini   # minimize 和温度初始化
    │   └─ in.crack1-aniso-rlx   # 施加位移后 relax

process.py             # 计算裂纹长度，检测临界事件的发生
