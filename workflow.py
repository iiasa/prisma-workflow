from pathlib import Path

import pyam
from climate_processor import MAGICCProcessor, MAGICCRunType, Workflow
from climate_processor.gcages_wrapper import SCI_OUTPUT_VARIABLES_DIAGNOSTIC
from nomenclature import DataStructureDefinition, RegionProcessor, process

here = Path(__file__).absolute().parent


def main(df: pyam.IamDataFrame) -> pyam.IamDataFrame:
    """Project/instance-specific workflow for scenario processing"""

    # Run the validation and region-processing
    definition = DataStructureDefinition(here / "definitions")

    return process(
        df,
        definition,
        processor=[
            RegionProcessor.from_directory(path=here / "mappings", dsd=definition),
            MAGICCProcessor(
                workflow=Workflow.SCI_V2_2_ALPHA,
                run_type=MAGICCRunType.COMPLETE,
                magicc_worker_number=4,
                magicc_variables=SCI_OUTPUT_VARIABLES_DIAGNOSTIC,
                include_input_data=True,
            ),
        ],
    )
