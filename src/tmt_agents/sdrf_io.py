"""Build an SDRF-Proteomics table from a simple sample sheet.

The sample sheet has one row per TMT channel with five columns:
sample_id, treatment, biological_replicate, antibody, channel.

Run-level parameters (instrument, enzyme, modifications, ...) are passed
separately. Values marked as assumptions in RUN_PARAMS_OWN_DESIGN have not
been confirmed with the mass spectrometry facility.
"""

from pathlib import Path

import pandas as pd

# Run-level parameters for the EZH2/IgG x CPI-169/DMSO experiment.
# Every entry except the enzyme is an ASSUMPTION pending confirmation
# with the Protein and Proteomics Centre (PPC).
RUN_PARAMS_OWN_DESIGN = {
    "organism": "homo sapiens",
    "cell_line": "RL",
    "cellosaurus_accession": "CVCL_1660",
    "disease": "diffuse large B-cell lymphoma",
    "data_file": "EZH2_IgG_CPI169_TMTpro16.raw",  # placeholder file name
    "fraction": "1",  # assumption: single-shot, no fractionation
    "instrument": "NT=Orbitrap Exploris 480;AC=MS:1003028",  # assumption
    "dissociation": "NT=HCD;AC=PRIDE:0000590",  # assumption
    "acquisition": "NT=Data-Dependent Acquisition;AC=PRIDE:0000627",  # assumption
    "enzyme": "NT=Trypsin;AC=MS:1001251",  # stated in thesis (on-bead digestion)
    "modifications": [  # assumption: standard TMTpro settings
        "NT=TMTpro;AC=UNIMOD:2016;TA=K;MT=Fixed",
        "NT=TMTpro;AC=UNIMOD:2016;PP=Any N-term;MT=Fixed",
        "NT=Carbamidomethyl;AC=UNIMOD:4;TA=C;MT=Fixed",
        "NT=Oxidation;AC=UNIMOD:35;TA=M;MT=Variable",
    ],
    "precursor_tolerance": "10 ppm",  # assumption
    "fragment_tolerance": "0.02 Da",  # assumption
}

SAMPLE_SHEET_COLUMNS = [
    "sample_id",
    "treatment",
    "biological_replicate",
    "antibody",
    "channel",
]


def read_sample_sheet(path: str | Path) -> pd.DataFrame:
    """Read the sample sheet and check that the expected columns exist."""
    sheet = pd.read_csv(path, dtype=str)
    missing = [c for c in SAMPLE_SHEET_COLUMNS if c not in sheet.columns]
    if missing:
        raise ValueError(f"Sample sheet is missing columns: {missing}")
    return sheet


def build_sdrf(sheet: pd.DataFrame, params: dict) -> pd.DataFrame:
    """Return an SDRF table with one row per labelled channel.

    Unused TMT channels are not written as rows.
    """
    rows = []
    for s in sheet.itertuples(index=False):
        row = [
            ("source name", s.sample_id),
            ("characteristics[organism]", params["organism"]),
            ("characteristics[organism part]", "not applicable"),
            ("characteristics[cell line]", params["cell_line"]),
            ("characteristics[cellosaurus accession]", params["cellosaurus_accession"]),
            ("characteristics[cellosaurus name]", params["cell_line"]),
            ("characteristics[disease]", params["disease"]),
            ("characteristics[biological replicate]", s.biological_replicate),
            ("characteristics[compound]", s.treatment),
            ("characteristics[antibody]", s.antibody),
            ("assay name", "run1"),
            ("technology type", "proteomic profiling by mass spectrometry"),
            ("comment[data file]", params["data_file"]),
            ("comment[fraction identifier]", params["fraction"]),
            ("comment[technical replicate]", "1"),
            ("comment[label]", s.channel),
            ("comment[instrument]", params["instrument"]),
            ("comment[proteomics data acquisition method]", params["acquisition"]),
            ("comment[dissociation method]", params["dissociation"]),
            ("comment[cleavage agent details]", params["enzyme"]),
        ]
        row += [("comment[modification parameters]", m) for m in params["modifications"]]
        row += [
            ("comment[precursor mass tolerance]", params["precursor_tolerance"]),
            ("comment[fragment mass tolerance]", params["fragment_tolerance"]),
            ("factor value[compound]", s.treatment),
            ("factor value[antibody]", s.antibody),
        ]
        rows.append(row)

    # SDRF allows repeated column names (e.g. several modification columns),
    # so build the frame from positional values rather than a dict.
    columns = [name for name, _ in rows[0]]
    values = [[v for _, v in r] for r in rows]
    return pd.DataFrame(values, columns=columns)


def write_sdrf(sdrf: pd.DataFrame, path: str | Path) -> None:
    """Write the SDRF as a tab-separated file."""
    sdrf.to_csv(path, sep="\t", index=False)


def read_sdrf(path: str | Path) -> pd.DataFrame:
    """Read an SDRF, keeping repeated column names as they appear in the file."""
    with open(path, encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
    sdrf = pd.read_csv(path, sep="\t", dtype=str, header=0)
    sdrf.columns = header  # undo pandas' ".1" suffixes on repeated names
    return sdrf
