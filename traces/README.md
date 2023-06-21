# Sieve traces
Using Nvidia RTX 3080 and CUDA 11.6, the following Accel-Sim compatible traces are available:

| Parboil |   Rodinia  |     CUDA SDK     | Cactus | MLPerf v2.0 (Inference)  | MLPerf v2.0 (Train) |
|:-------:|:----------:|:----------------:|:------:|:------------------------:|:-------------------:|
|  cutcp  |     cfd    |   blackscholes   |   gms  |          3d-unet         |       3d-unet       |
|  histo  |  heartwall |      dct8x8      |   gru  |           bert           |         bert        |
|   lbm   |  histogram |     gradient     |   gst  |         resnet50         |                     |
|   spmv  |  hotspot3d |   hsopticalflow  |   dcg  |       ssd-mobilenet      |                     |
| stencil |   huffman  |     mergesort    |   nst  |       ssd-resnet34       |                     |
|         |     nw     |      nvjpeg      |   spt  |                          |                     |
|         | pathfinder |      random      |        |                          |                     |
|         |    srad    |       scan       |        |                          |                     |
|         |            | sorting networks |        |                          |                     |
|         |            |    fast walsh    |        |                          |                     |

Use the modified Accel-Sim tracer to create your own traces. All traces are available here:

[https://cactus.elis.ugent.be/traces](https://cactus.elis.ugent.be/traces)
