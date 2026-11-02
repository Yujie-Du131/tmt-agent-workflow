# QC on quantms output: PXD000001 (quantms test_tmt)

Input: `data/quantms_pxd000001/msstats_in.csv.gz` (16278 rows; 473 proteins; 468 proteins after removing decoys and protein groups).

## Channel metrics (background proteins only)

|     |   n_quantified |   raw_median |   raw_median_z |   corr_to_others |
|:----|---------------:|-------------:|---------------:|-----------------:|
| ch1 |            465 |       20.447 |          0.405 |              nan |
| ch2 |              1 |       11.363 |        -34.49  |              nan |
| ch3 |            468 |       20.587 |          0.944 |              nan |
| ch4 |              4 |       13.187 |        -27.485 |              nan |
| ch5 |            468 |       20.264 |         -0.299 |              nan |
| ch6 |            468 |       20.419 |          0.299 |              nan |

## Spike-in ratio recovery

Slope of measured on expected centred log2 values (1 = full recovery; below 1 = ratio compression).

| accession   | protein              |   psms |   expected_range_log2 |   slope |
|:------------|:---------------------|-------:|----------------------:|--------:|
| P00924      | sp|P00924|ENO1_YEAST |     31 |                 3.322 |   0.882 |
| P02769      | sp|P02769|ALBU_BOVIN |     31 |                 3.322 |   0.74  |
| P00489      | sp|P00489|PYGM_RABIT |     48 |                 1     |   0.753 |
| P62894      | sp|P62894|CYC_BOVIN  |      3 |                 1     |   1.156 |

Pooled slope over all identified spike-ins: **0.82**
