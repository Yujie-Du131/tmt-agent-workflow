#!/usr/bin/env bash -C -e -u -o pipefail
IsobaricWorkflow \
    -threads 2 \
    -in TMT_Erwinia_1uLSike_Top10HCD_isol2_45stepped_60min_01.mzML \
    -in_id TMT_Erwinia_1uLSike_Top10HCD_isol2_45stepped_60min_01_clean_perc.idparquet \
    -exp_design PXD000001.sdrf_openms_design.tsv \
    -type tmt6plex \
    -inference_method aggregation \
    -protein_quantification unique_peptides \
    -psmFDR 1.0 \
    -proteinFDR 0.01 \
    -picked_fdr true \
    -picked_decoy_string rev \
    -extraction:min_precursor_purity 0.0 \
    -extraction:precursor_isotope_deviation 10.0 \
    -extraction:min_reporter_intensity 0.0 \
     \
    -out PXD000001.sdrf_openms_design_openms.consensusXML \
    -out_mzTab PXD000001.sdrf_openms_design_openms.mzTab \
    -out_qpx PXD000001.sdrf_openms_design_qpx \
    -extraction:reporter_mass_shift 0.01 \
    2>&1 | tee isobaricworkflow.log
cat <<-END_VERSIONS > versions.yml
"BIGBIO_QUANTMS:QUANTMS:TMT:ISOBARIC_WORKFLOW":
    IsobaricWorkflow: $(IsobaricWorkflow 2>&1 | grep -E '^Version(.*)' | sed 's/Version: //g' | cut -d ' ' -f 1)
END_VERSIONS
