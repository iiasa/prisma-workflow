import ixmp4
from climate_processor import MAGICCProcessor, MAGICCRunType, Workflow
from pyam.ixmp4 import read_run

runs = ixmp4.Platform("prisma-internal").runs.list()

applicable_runs = [
    run
    for run in runs
    if run.scenario.name.startswith("SSP") and "ICT" not in run.scenario.name
]

print(f"Found {len(applicable_runs)} applicable runs for processing.")

for run in applicable_runs:
    try:
        print(f"Processing run: {run.model.name} | {run.scenario.name}")
        input_data = read_run(run, variable="Emissions*", region="World")

        # special handling only for GEM-E3
        if "GEM-E3" in run.model.name:
            input_data = input_data.interpolate(2020)
            input_data.subtract(
                "Emissions|CO2",
                "Emissions|CO2|Energy and Industrial Processes",
                "Emissions|CO2|AFOLU",
                append=True,
            )
        output_data = MAGICCProcessor(
            run_type=MAGICCRunType.COMPLETE,
            workflow=Workflow.SCI,
            magicc_variables=[
                "Climate Assessment|Harmonized and Infilled|Emissions|CO2|AFOLU [SCI v1.1]",
                "Climate Assessment|Harmonized and Infilled|Emissions|CO2|Energy and Industrial Processes [SCI v1.1]",
                "Climate Assessment|Surface Temperature (GSAT)|33rd Percentile [MAGICC v7.6.0a3]",
                "Climate Assessment|Surface Temperature (GSAT)|67th Percentile [MAGICC v7.6.0a3]",
                "Climate Assessment|Surface Temperature (GSAT)|Median [MAGICC v7.6.0a3]",
                "Climate Assessment|Harmonized and Infilled|Emissions|N2O [SCI v1.1]",
                "Climate Assessment|Harmonized and Infilled|Emissions|CH4 [SCI v1.1]",
                "Climate Assessment|Harmonized and Infilled|Emissions|Kyoto Gases (AR6-GWP100) [SCI v1.1]",
            ],
        ).apply(input_data)

        with run.transact("Import climate assessment"):
            run.iamc.add(output_data.data)
            for name, value in output_data.meta.T.iterrows():
                if name.startswith("Climate Assessment"):
                    run.meta[name] = value.values[0]
            print(run.model.name + " | " + run.scenario.name)
    except Exception as e:
        with open(run.model.name + "_" + run.scenario.name + "_error.txt", "w") as f:
            f.write(str(e))
