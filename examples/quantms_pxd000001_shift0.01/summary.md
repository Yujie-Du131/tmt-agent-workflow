# QC on quantms output: PXD000001 (quantms test_tmt)

Input: `data/quantms_pxd000001/msstats_in_shift0.01.csv.gz` (17052 rows; 468 proteins; 463 proteins after removing decoys and protein groups).

## Channel metrics (background proteins only)

|     |   n_quantified |   raw_median |   raw_median_z |   corr_to_others |
|:----|---------------:|-------------:|---------------:|-----------------:|
| ch1 |            460 |       20.75  |          1.3   |            0.999 |
| ch2 |            459 |       20.602 |         -0.235 |            0.995 |
| ch3 |            463 |       20.732 |          1.114 |            0.999 |
| ch4 |            461 |       20.605 |         -0.203 |            0.997 |
| ch5 |            463 |       20.451 |         -1.798 |            0.999 |
| ch6 |            463 |       20.644 |          0.203 |            0.999 |

## Spike-in ratio recovery

Slope of measured on expected centred log2 values (1 = full recovery; below 1 = ratio compression).

| accession   | protein              |   psms |   expected_range_log2 |   slope |
|:------------|:---------------------|-------:|----------------------:|--------:|
| P00924      | sp|P00924|ENO1_YEAST |     32 |                 3.322 |   0.798 |
| P02769      | sp|P02769|ALBU_BOVIN |     32 |                 3.322 |   0.729 |
| P00489      | sp|P00489|PYGM_RABIT |     52 |                 1     |   0.753 |
| P62894      | sp|P62894|CYC_BOVIN  |      3 |                 1     |   1.152 |

Pooled slope over all identified spike-ins: **0.778**
