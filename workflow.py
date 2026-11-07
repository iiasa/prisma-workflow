from pathlib import Path

import pyam
from nomenclature import DataStructureDefinition, RegionProcessor, process
from scenariocompass import ScenarioCompassProcessor

try:
    from climate_processor import MAGICCProcessor, MAGICCRunType, Workflow
    from climate_processor.gcages_wrapper import SCI_OUTPUT_VARIABLES_DIAGNOSTIC

    FOUND_MAGICC = True
except ImportError:
    FOUND_MAGICC = False

here = Path(__file__).absolute().parent


def main(df: pyam.IamDataFrame) -> pyam.IamDataFrame:
    """Project/instance-specific workflow for scenario processing"""

    # Run the validation and region-processing
    definition = DataStructureDefinition(here / "definitions")

    df = process(
        df,
        definition,
        processor=[
            RegionProcessor.from_directory(here / "mappings", definition),
            ScenarioCompassProcessor(),
        ],
    )

    if FOUND_MAGICC:
        df = df.filter(region="World", keep=False).append(
            MAGICCProcessor(
                workflow=Workflow.SCI_V2_2_ALPHA,
                run_type=MAGICCRunType.COMPLETE,
                magicc_worker_number=4,
                magicc_variables=SCI_OUTPUT_VARIABLES_DIAGNOSTIC,
                include_input_data=True,
            ).apply(df.filter(region="World"))
        )
        # manual fix for https://github.com/iiasa/climate-processor/issues/105
        df.rename(unit={"GtC / yr": "Gt C/yr"}, inplace=True)
        df.rename(unit={"GtC/yr": "Gt C/yr"}, inplace=True)
        df.rename(unit={"MtCH4/yr": "Mt CH4/yr"}, inplace=True)

    return df
