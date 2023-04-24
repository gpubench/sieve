# Sieve
This repository contains supplementary meterials described in the following paper:
```
Mahmood Naderan-Tahan, Hossein SeyyedAghaei and Lieven Eeckhout, 
"Sieve: Stratified GPU-Compute Workload Sampling", 
in Proceedings of the IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS), 
pp.224-234, 2023.
```

## Introduction

Since modern GPU applications have complex software stacks, architectural simulation becomes more challenging and time consuming. With Sieve, it is possible to select and simulate representative kernel invocations instead of all invocations. This repository contains main scripts to find representative kernel invocations in an application as well as publicly released traces used in the paper. All traces are simulatable with [Accel-Sim](https://github.com/accel-sim/accel-sim-framework "Accel-Sim") and the traces were generated using a modified version of Accel-Sim tracer on an Nvidia RTX 3080.

## How to use scripts?
Please see the readme file in `scripts/` folder.

## How to use trace files?
Please see the readme file in `traces/` folder.

## How to cite?
If you use the scripts from this repository, please cite the Sieve paper. If you use Cactus traces from this repository, please cite the Cactus paper as well.

```
Mahmood Naderan-Tahan, Hossein SeyyedAghaei and Lieven Eeckhout, 
"Sieve: Stratified GPU-Compute Workload Sampling", 
in Proceedings of the IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS), 
pp.224-234, 2023.

Mahmood Naderan-Tahan and Lieven Eeckhout, 
"Cactus: Top-Down GPU-Compute Benchmarking using Real-Life Applications", 
in Proceedings of the IEEE International Symposium on Workload Characterization (IISWC), 
pp. 176-188, 2021.
```
