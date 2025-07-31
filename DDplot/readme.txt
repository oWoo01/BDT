step1: 使用xtal调用BCC生成<elem>-perf.cfg
step2: 用atomsk将<elem>-perf.cfg转为<elem>-perf.lmp
step3: in.disl-generate生成minimize之后完美的和有位错的<elem>*.cfg
step4: 使用atomsk将cfg转为lmp
step5：调用ddplot.py生成ddmap，检查位错核心结构为Dcore or NDcore

step3-5被包括在batch-run.sh当中

DDplot/
├── batch-run.sh
├── BCC
├── ddplot.py
├── in.disl_generate
├── readme.txt
├── <elem>-perf.cfg
└── potentials/
    └── <elem>/
        ├── <elem>-perf.lmp
        ├── potential-list.txt
        ├── log.lammps
        └── <potential type>-<potential name>
            ├── library.meam
            ├── Nb.meam
            ├── <elem*>.cfg
            ├── <file_perf>.lmp
            ├── <file_disl>.lmp
            └── ddmap.png
