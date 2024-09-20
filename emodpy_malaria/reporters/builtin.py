from dataclasses import dataclass, field

from emodpy.reporters.base import BuiltInReporter
from emod_api import schema_to_class as s2c
import emod_api.interventions.utils as utils


def add_report_vector_genetics(task, manifest, start_day: int = 0, duration_days: int = 365000,
                               nodes: list = None,
                               species: str = None, gender: str = "VECTOR_FEMALE",
                               include_vector_state: int = 1, stratify_by: str = "GENOME",
                               combine_similar_genomes: int = 0,
                               specific_genome_combinations_for_stratification: list = None,
                               allele_combinations_for_stratification: list = None,
                               alleles_for_stratification: list = None,
                               report_description: str = ""):
    """
    Adds ReportVectorGenetics to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start reporting data
        duration_days: number of days over which to report data
        nodes: the list of nodes in which to collect data, empty or None means all nodes
        species: the species to include information on
        gender: gender of species to include information on. Default: "VECTOR_FEMALE",
            other options: "VECTOR_MALE", "VECTOR_BOTH_GENDERS"
        include_vector_state: if 1(true), adds the columns for vectors in the different states (i.e Eggs, Larva, etc)
        stratify_by: the way to stratify data. Default: "GENOME",
            other options: "SPECIFIC_GENOME", "ALLELE", "ALLELE_FREQ"
        combine_similar_genomes: if 1(true), genomes are combined if for each locus (ignoring gender) the set of allele
            of the two genomes are the same (i.e. 1-0 is similar to 0-1). Depends on: "GENOME", "SPECIFIC_GENOME"
            specific_genome_combinations_for_stratification: if stratifying by "SPECIFIC_GENOME", then use these genomes
            to stratify by. Example::

                [{"Allele_Combination": [[ "a0",  "*" ], [ "b1", "b0" ]]},
                {"Allele_Combination": [[ "a1", "a0" ], [ "b0",  "*" ]]}]

        allele_combinations_for_stratification: if stratifying by "ALLELE", then also add these allele name
            combos to the stratification, Example::

                [[ "a0", "b0" ], [ "a1", "b1" ]]

        alleles_for_stratification: For example::

            [ "a0", "a1", "b0", "b1" ]

        report_description: adds the description to the filename of the report to differentiate it from others

    Returns:
        Nothing
    """
    # verifying that there are alleles to report on
    if task and not task.config.parameters.Vector_Species_Params:  # else assume we're in unittest
        raise ValueError(f"No Vector_Species_Params defined. You need to define at least one to "
                         f"use ReportVectorGenetics.\n")

    reporter = ReportVectorGenetics()  # Create the reporter

    def rec_config_builder(params):
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        params.Species = species
        params.Gender = gender
        params.Include_Vector_State_Columns = include_vector_state
        params.Stratify_By = stratify_by
        if stratify_by == "GENOME" or stratify_by == "SPECIFIC_GENOME":
            params.Combine_Similar_Genomes = combine_similar_genomes
        if stratify_by == "SPECIFIC_GENOME":
            params.Specific_Genome_Combinations_For_Stratification = specific_genome_combinations_for_stratification if specific_genome_combinations_for_stratification else []
        elif stratify_by == "ALLELE":
            params.Allele_Combinations_For_Stratification = allele_combinations_for_stratification if allele_combinations_for_stratification else []
        elif stratify_by == "ALLELE_FREQ":
            params.Alleles_For_Stratification = alleles_for_stratification if alleles_for_stratification else []
        params.Report_Description = report_description
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_vector_stats(task, manifest,
                            species_list: list = None,
                            stratify_by_species: int = 0,
                            include_wolbachia: int = 0,
                            include_gestation: int = 0):
    """
    Adds ReportVectorStats report to the simulation. See class definition for description of the report.
    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        species_list: a list of species to include information on
        stratify_by_species: if 1(true), data will break out each the species for each node
        include_wolbachia: if 1(true), add a column for each type of Wolbachia
        include_gestation: if 1(true), adds columns for feeding and gestation

    Returns:
        Nothing
    """
    if task and not task.config.parameters.Vector_Species_Params:
        raise ValueError(f"No Vector_Species_Params defined. You need to define at least one to "
                         f"use ReportVectorStats.\n")
    reporter = ReportVectorStats()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Species_List = species_list if species_list else []
        params.Stratify_By_Species = stratify_by_species
        params.Include_Wolbachia_Columns = include_wolbachia
        params.Include_Gestation_Columns = include_gestation
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_summary_report(task, manifest, start_day: int = 0, duration_days: int = 365000,
                               nodes: list = None, reporting_interval: float = 1,
                               age_bins: list = None, individual_property_filter: str = "",
                               infectiousness_bins: list = None, max_number_reports: int = 100,
                               parasitemia_bins: list = None,
                               pretty_format: int = 0,
                               report_description: str = ""):
    """
    Adds MalariaSummaryReport to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to starts collecting data for the report
        duration_days: The duration of simulation days over which to report events. The report will stop collecting
            data when the simulation day is greater than Start_Day + Duration_Days.
        nodes: a list of nodes from which to collect data for the report
        reporting_interval: Defines the cadence of the report by specifying how many time steps to collect data
            before writing to the file
        age_bins: The max age in years per bin, listed in ascending order. Use a large value for the last bin,
            to collect all remaining individuals
        individual_property_filter: the individual 'property:value' to filter on. The default of an empty string
            means the report is not filtered.  Example: "Risk:HIGH"
        infectiousness_bins: infectiousness Bins to aggregate within for the report
        max_number_reports: the maximum number of report output files that will be produced for a given simulation
        parasitemia_bins: Parasitemia bins on which to aggregate. A value <= 0 in the first bin indicates that
            uninfected individuals are added to this bin. You must sort your input data from low to high.
        pretty_format: if 1(true) sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line.
        report_description:  adds the description to the filename of the report to differentiate it from others

    Returns:
        Nothing
    """

    reporter = MalariaSummaryReport()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        params.Age_Bins = age_bins if age_bins else []
        params.Individual_Property_Filter = individual_property_filter
        params.Infectiousness_Bins = infectiousness_bins if infectiousness_bins else []
        params.Max_Number_Reports = max_number_reports
        params.Parasitemia_Bins = parasitemia_bins if infectiousness_bins else []
        params.Pretty_Format = pretty_format
        params.Reporting_Interval = reporting_interval
        params.Report_Description = report_description
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_patient_json_report(task, manifest):
    """
    Adds MalariaPatientJSONReport report to the simulation. See class definition for description of the report.
    You do not need to configure any data parameters to generate this report.
    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file

    Returns:
        Nothing
    """

    reporter = MalariaPatientJSONReport()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_transmission_report(task, manifest,
                                    start_day: int = 0,
                                    duration_days: int = 365000,
                                    nodes: list = None,
                                    pretty_format: int = 0,
                                    report_description: str = ""):
    """
    Adds ReportSimpleMalariaTransmissionJSON report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day to start collecting data for the report.
        duration_days: The duration of simulation days over which to report events. The report will stop
            collecting data when the simulation day is greater than Start_Day + Duration_Days
        nodes: list of nodes for which to collect data for the report
        pretty_format: if 1(true) sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line.
        report_description: adds the description to the filename of the report to differentiate it from others

    Returns:
        Nothing
    """

    reporter = ReportSimpleMalariaTransmissionJSON()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        params.Pretty_Format = pretty_format
        params.Report_Description = report_description
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_malaria_filtered(task, manifest,
                                start_day: int = 0,
                                end_day: int = 365000,
                                nodes: list = None,
                                report_filename: str = "ReportMalariaFiltered.json",
                                min_age_years: float = 0,
                                max_age_years: float = 125,
                                has_interventions: list = None,
                                include_30day_avg_infection_duration: bool = True):
    """
    Adds ReportMalariaFiltered report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day:  the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        nodes: list of nodes for which to collect the data, None or [] collects all the nodes
        report_filename: name of the file to be written
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        has_interventions: A channel is added to the report for each InterventionName provided.  The channel name
            will be Has_<InterventionName> and will be the fraction of the population that has that intervention.
            The **Intervention_Name** in the campaign should be the values in this parameter
        include_30day_avg_infection_duration: If set to True (1), the 30-Day Avg Infection channel is included in the
            report

    Returns:
        Nothing
    """

    reporter = ReportMalariaFiltered()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Node_IDs_Of_Interest = nodes if nodes else []
        params.Report_File_Name = report_filename
        params.Has_Interventions = has_interventions if has_interventions else []
        params.Include_30Day_Avg_Infection_Duration = 1 if include_30day_avg_infection_duration else 0
        params.Max_Age_Years = max_age_years
        params.Min_Age_Years = min_age_years
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_spatial_report_malaria_filtered(task, manifest,
                                        start_day: int = 0,
                                        end_day: int = 365000,
                                        reporting_interval: int = 1,
                                        nodes: list = None,
                                        report_filename: str = "SpatialReportMalariaFiltered",
                                        spatial_output_channels: list = None):
    """
    Adds SpatialReportMalariaFiltered report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day:  the day of the simulation to start collecting data
        end_day: the day of simulation to stop collecting data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data before
            writing to the file.
        nodes: list of nodes for which to collect the data
        report_filename: name of the file to be written
        spatial_output_channels: list of names of channels you want to have output for. Available channels are:
            "Adult_Vectors", "Air_Temperature", "Births", "Blood_Smear_Gametocyte_Prevalence",
            "Blood_Smear_Parasite_Prevalence", "Campaign_Cost", "Daily_Bites_Per_Human", "Daily_EIR", "Disease_Deaths",
            "Fever_Prevalence", "Human_Infectious_Reservoir", "Infected", "Infectious_Vectors", "Land_Temperature",
            "Mean_Parasitemia", "New_Clinical_Cases", "New_Infections", "New_Reported_Infections", "New_Severe_Cases",
            "PCR_Gametocyte_Prevalence", "PCR_Parasite_Prevalence", "PfHRP2_Prevalence", "Population", "Prevalence",
            "Rainfall", "Relative_Humidity", "True_Prevalence"
            Defaults: ["Blood_Smear_Parasite_Prevalence", "New_Clinical_Cases", "Population"]
    Returns:
        Nothing
    """

    reporter = SpatialReportMalariaFiltered()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Reporting_Interval = reporting_interval
        params.Node_IDs_Of_Interest = nodes if nodes else []
        params.Report_File_Name = report_filename
        params.Spatial_Output_Channels = spatial_output_channels if spatial_output_channels else [
            "Blood_Smear_Parasite_Prevalence",
            "New_Clinical_Cases",
            "Population"]
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_event_counter(task, manifest,
                             start_day: int = 0,
                             duration_days: int = 365000,
                             event_trigger_list: list = None,
                             nodes: list = None,
                             report_description: str = ""):
    """
    Adds ReportEventCounter report to the simulation.
    See class definition for description of the report.
    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start counting events
        duration_days: number of days for which to count events
        event_trigger_list: list of events which to count
        nodes: list of nodes in which to count the events
        report_description: used by reports and custom reports. Augments the filename of the report.
    Returns:
        Nothing
    """

    reporter = ReportEventCounter()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Event_Trigger_List = event_trigger_list if event_trigger_list else []
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        params.Report_Description = report_description
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_sql_report(task, manifest,
                           start_day: int = 0,
                           end_day: int = 365000,
                           include_infection_table: int = 1,
                           include_health_table: int = 1,
                           include_drug_table: int = 0):
    """
    Adds MalariaSqlReport report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data
        include_infection_table: if 1(true), include the table that provides data at each time step for each active
            infection
        include_health_table: if 1(true), include the table that provides data at each time step for a person's health
        include_drug_status: if 1(true), include the table that provides data at each time step for each drug used

    Returns:
        Nothing
    """

    reporter = MalariaSqlReport()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.End_Day = end_day
        params.Include_Infection_Data_Table = include_infection_table
        params.Include_Health_Table = include_health_table
        params.Include_Drug_Status_Table = include_drug_table
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_vector_habitat_report(task, manifest):
    """
    Adds VectorHabitatReport report to the simulation. See class definition for description of the report.
    You do not need to configure any data parameters to generate this report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file

    Returns:
        Nothing
    """

    if task and not task.config.parameters.Vector_Species_Params:  # else assume we're in unittest
        raise ValueError(f"No Vector_Species_Params defined. You need to define at least one to "
                         f"use VectorHabitatReport.\n")

    reporter = VectorHabitatReport()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_immunity_report(task, manifest,
                                start_day: int = 0,
                                duration_days: int = 365000,
                                reporting_interval: int = 1,
                                max_number_reports: int = 365000,
                                nodes: list = None,
                                age_bins: list = None,
                                pretty_format: int = 0,
                                report_description: str = ""):
    """
    Adds MalariaImmunityReport report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        duration_days: number of days over which to report data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data before
            writing to the file.
        max_number_reports: the maximum number of report output files that will be produced for a given simulation
        nodes: list of nodes for which to collect data
        age_bins: The max age in years per bin, listed in ascending order. Use a large value for the last bin,
            to collect all remaining individuals
        pretty_format: if 1(true) sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line.
        report_description: adds the description to the filename of the report to differentiate it from others

    Returns:
        Nothing
    """

    reporter = MalariaImmunityReport()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Reporting_Interval = reporting_interval
        params.Max_Number_Reports = max_number_reports
        params.Age_Bins = age_bins if age_bins else []
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        params.Pretty_Format = pretty_format
        params.Report_Description = report_description

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_malaria_survey_analyzer(task, manifest,
                                start_day: int = 0,
                                duration_days: int = 365000,
                                event_trigger_list: list = None,
                                reporting_interval: float = 1,
                                max_number_reports: int = 365000,
                                nodes: list = None,
                                individual_property_to_collect: str = "",
                                pretty_format: int = 0,
                                report_description: str = ""):
    """
    Adds MalariaSurveyJSONAnalyzer report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        duration_days: number of days over which to report data
        reporting_interval: defines the cadence of the report by specifying how many time steps to collect data
            before writing to the file
        event_trigger_list: list of individual events to include into the report
        max_number_reports: the maximum number of report output files that will be produced for a given simulation
        nodes: list of nodes for which to collect data
        individual_property_to_collect: name of the Individual Property Key whose value to collect.  Empty string means
            collect values for all Individual Properties
        pretty_format: if 1(true) sets pretty JSON formatting, which includes carriage returns, line feeds, and spaces
            for easier readability. The default, 0 (false), saves space where everything is on one line
        report_description: adds the description to the filename of the report to differentiate it from others

    Returns:

    """
    if not event_trigger_list:
        raise ValueError("event_trigger_list cannot be empty, please define individual"
                         " events to include into the report.\n")

    reporter = MalariaSurveyJSONAnalyzer()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Max_Number_Reports = max_number_reports
        params.Event_Trigger_List = event_trigger_list if event_trigger_list else []
        params.IP_Key_To_Collect = individual_property_to_collect
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        params.Pretty_Format = pretty_format
        params.Reporting_Interval = reporting_interval
        params.Report_Description = report_description

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_drug_status_report(task, manifest,
                           start_day: int = 0,
                           end_day: int = 365000):
    """
    Adds ReportDrugStatus report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data

    Returns:
        Nothing
    """

    reporter = ReportDrugStatus()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.End_Day = end_day

        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_human_migration_tracking(task, manifest):
    """
    Adds ReportHumanMigrationTracking report to the simulation.
    There are no special parameter that need to be configured to generate the report. However, the simulation
    must have migration enabled.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file

    Returns:
        Nothing
    """

    reporter = ReportHumanMigrationTracking()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_node_demographics(task, manifest,
                                 age_bins: list = None,
                                 individual_property_to_collect: str = "",
                                 stratify_by_gender: int = 1):
    """
    Adds ReportNodeDemographics report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        age_bins: the age bins (in years) to aggregate within and report. An empty array does not stratify by age. You
            must sort your input data from low to high.
        individual_property_to_collect: The name of theIndividualProperties key by which to stratify the report.
            An empty string does not stratify by Individual Properties
        stratify_by_gender: if 1(true), to stratify by gender. Set to false (0) to not stratify by gender.

    Returns:
        Nothing
    """

    reporter = ReportNodeDemographics()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.IP_Key_To_Collect = individual_property_to_collect
        params.Age_Bins = age_bins if age_bins else []
        params.Stratify_By_Gender = stratify_by_gender
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_node_demographics_malaria(task, manifest,
                                         age_bins: list = None,
                                         individual_property_to_collect: str = "",
                                         stratify_by_gender: int = 1):
    """
    Adds ReportNodeDemographicsMalaria report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        age_bins: the age bins (in years) to aggregate within and report. An empty array does not stratify by age. You
            must sort your input data from low to high.
        individual_property_to_collect: The name of theIndividualProperties key by which to stratify the report.
            An empty string does not stratify by Individual Properties
        stratify_by_gender: if 1(true), to stratify by gender. Set to false (0) to not stratify by gender.

    Returns:
        Nothing
    """

    reporter = ReportNodeDemographicsMalaria()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.IP_Key_To_Collect = individual_property_to_collect
        params.Age_Bins = age_bins if age_bins else []
        params.Stratify_By_Gender = stratify_by_gender
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_node_demographics_malaria_genetics(task, manifest,
                                                  barcodes: list = None,
                                                  drug_resistant_strings: list = None,
                                                  drug_resistant_statistic_type: str = "NUM_PEOPLE_WITH_RESISTANT_INFECTION",
                                                  age_bins: list = None,
                                                  individual_property_to_collect: str = "",
                                                  stratify_by_gender: int = 1):
    """
    Adds ReportNodeDemographicsMalariaGenetics report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        barcodes: a list of barcode strings. The report contains the number of human infections with each barcode.
            Use '*' for a wild card at a loci to include all values at that loci.  For example, “A*T” includes AAT,
            ACT, AGT, and ATT. The report contains a BarcodeOther column for barcodes that are not defined.
            Note: There is no validation that the barcode strings are valid barcodes for the scenario.
        drug_resistant_strings: a list of strings representing the set of drug resistant markers.  A column will be
            created with the number of humans infetions with that barcode.  One can use '*' for a wild card.
            A 'BarcodeOther' column will be created for barcodes not define
        drug_resistant_statistic_type: indicates the statistic in the Drug Resistant columns:
            NUM_PEOPLE_WITH_RESISTANT_INFECTION = A person is counted if they have one infection with that drug
            resistant marker;
            NUM_INFECTIONS = The total number of infections with that marker.
        age_bins: the age bins (in years) to aggregate within and report. An empty array does not stratify by age. You
            must sort your input data from low to high.
        individual_property_to_collect: The name of theIndividualProperties key by which to stratify the report.
            An empty string does not stratify by Individual Properties
        stratify_by_gender: if 1(true), to stratify by gender. Set to false (0) to not stratify by gender.

    Returns:
        Nothing
    """

    reporter = ReportNodeDemographicsMalariaGenetics()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.IP_Key_To_Collect = individual_property_to_collect
        params.Age_Bins = age_bins if age_bins else []
        params.Stratify_By_Gender = stratify_by_gender
        params.Barcodes = barcodes if barcodes else []
        params.Drug_Resistant_Strings = drug_resistant_strings if drug_resistant_strings else []
        params.Drug_Resistant_Statistic_Type = drug_resistant_statistic_type
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_vector_migration(task, manifest,
                                start_day: int = 0, end_day: int = 365000):
    """
    Adds ReportVectorMigration report to the simulation.
    See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        start_day: the day of the simulation to start collecting data
        end_day: the day of the simulation to stop collecting data

    Returns:
        Nothing
    """

    if task and not task.config.parameters.Vector_Species_Params:  # else assume we're in unittest
        raise ValueError(f"No Vector_Species_Params defined.\n")

    reporter = ReportVectorMigration()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.End_Day = end_day
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_report_vector_stats_malaria_genetics(task, manifest,
                                             species_list: list = None,
                                             stratify_by_species: int = 0,
                                             include_wolbachia: int = 0,
                                             include_gestation: int = 0,
                                             barcodes: list = None):
    """
    Adds ReportVectorStatsMalariaGenetics report to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: schema path file
        species_list: a list of species to include information on
        stratify_by_species: if 1(true), data will break out each the species for each node
        include_wolbachia: if 1(true), add a column for each type of Wolbachia
        include_gestation: if 1(true), adds columns for feeding and gestation
        barcodes: a list of barcode strings. The report contains the number of human infections with each barcode.
            Use '*' for a wild card at a loci to include all values at that loci.  For example, “A*T” includes AAT,
            ACT, AGT, and ATT. The report contains a BarcodeOther column for barcodes that are not defined.
            Note: There is no validation that the barcode strings are valid barcodes for the scenario.
    Returns:
        Nothing
    """

    if task and not task.config.parameters.Vector_Species_Params:  # else assume we're in unittest
        raise ValueError(f"No Vector_Species_Params defined.\n")

    reporter = ReportVectorStatsMalariaGenetics()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Species_List = species_list if species_list else []
        params.Stratify_By_Species = stratify_by_species
        params.Include_Wolbachia_Columns = include_wolbachia
        params.Include_Gestation_Columns = include_gestation
        params.Barcodes = barcodes if barcodes else []
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


def add_event_recorder(task, event_list: list = None, only_include_events_in_list: bool = True,
                       ips_to_record: list = None,
                       start_day: int = 0, end_day: int = 365000, node_ids: list = None, min_age_years: float = 0,
                       max_age_years: float = 365000, must_have_ip_key_value: str = "",
                       must_have_intervention: str = "",
                       property_change_ip_to_record: str = ""):
    """
    Adds ReportEventRecorder report to the simulation. See class definition for description of the report.

    Args:
        task: task to which to add the reporter
        event_list: a list of events to record or exclude, depending on value of only_include_events_in_list
        only_include_events_in_list: if True, only record events listed.  if False, record ALL events EXCEPT for the
            ones listed
        ips_to_record: list of individual properties to include in report
        start_day: The day of the simulation to start collecting data
        end_day: The day of the simulation to stop collecting data.
        node_ids: Data will be collected for the nodes in this list, if None - all nodes have data collected.
        min_age_years: Minimum age in years of people to collect data on
        max_age_years: Maximum age in years of people to collect data on
        must_have_ip_key_value: A Key:Value pair that the individual must have in order to be included. Empty string
            means don't look at IndividualProperties
        must_have_intervention: The name of the an intervention that the person must have in order to be included.
            Empty string means don't look at the interventions
        property_change_ip_to_record:If the string is not empty, then the recorder will add the PropertyChange event to the
            list of events that the report is listening to. However, it will only record the events where the property
            changed the value of the given key

    Returns:
        Nothing
    """
    # Documentation: https://docs.idmod.org/projects/emod-malaria/en/latest/software-report-event-recorder.html
    if not event_list:
        if only_include_events_in_list:
            raise ValueError("Please define event_list parameter.\n")
        else:
            event_list = []

    task.config.parameters.Report_Event_Recorder = 1
    task.config.parameters.Report_Event_Recorder_Events = event_list
    task.config.parameters.Report_Event_Recorder_Individual_Properties = ips_to_record if ips_to_record else []
    task.config.parameters.Report_Event_Recorder_Start_Day = start_day
    task.config.parameters.Report_Event_Recorder_End_Day = end_day
    task.config.parameters.Report_Event_Recorder_Node_IDs_Of_Interest = node_ids if node_ids else []
    task.config.parameters.Report_Event_Recorder_Min_Age_Years = min_age_years
    task.config.parameters.Report_Event_Recorder_Max_Age_Years = max_age_years
    task.config.parameters.Report_Event_Recorder_Must_Have_IP_Key_Value = must_have_ip_key_value
    task.config.parameters.Report_Event_Recorder_Must_Have_Intervention = must_have_intervention
    task.config.parameters.Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest = property_change_ip_to_record
    task.config.parameters.Report_Event_Recorder_Ignore_Events_In_List = 0 if only_include_events_in_list else 1


def add_report_intervention_pop_avg(task, manifest,
                                    start_day: int = 0,
                                    duration_days: int = 36500000,
                                    report_description: str = "",
                                    nodes: list = None):
    """
    Adds ReportInterventionPopAvg reporter. See class definition for description of the report.

    Args:
        task: Task to which to add the reporter, if left as None, reporter is returned (used for unittests)
        manifest: Schema path file
        start_day: The day of the simulation to start collecting data
        duration_days: The number of days over which to collect report data
        report_description: Augments the filename of the report. If multiple CSV reports are being generated,
            this allows you to distinguish among the multiple reports
        nodes: List of nodes for which to collect data

    Returns:
        Nothing
    """
    reporter = ReportInterventionPopAvg()  # Create the reporter

    def rec_config_builder(params):  # not used yet
        params.Start_Day = start_day
        params.Duration_Days = duration_days
        params.Report_Description = report_description
        params.Nodeset_Config = utils.do_nodes(manifest.schema_file, nodes)
        return params

    reporter.config(rec_config_builder, manifest)
    if task:
        task.reporters.add_reporter(reporter)
    else:  # assume we're running a unittest
        return reporter


@dataclass
class ReportVectorGenetics(BuiltInReporter):
    """
        The vector genetics report is a CSV-formatted report (ReportVectorGenetics.csv) that collects
        information on how many vectors of each genome/allele combination exist at each time, node,
        and vector state. Information can only be collected on one species per report.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorGenetics"  # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults("ReportVectorGenetics", manifest.schema_file)
        rvg_params = config_builder(rvg_params)
        rvg_params.finalize()
        rvg_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(rvg_params))


@dataclass
class ReportVectorStats(BuiltInReporter):
    """
        The vector statistics report is a CSV-formatted report (ReportVectorStats.csv) that provides detailed
        life-cycle data on the vectors in the simulation. The report is stratified by time, node ID,
        and (optionally) species.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorStats"  # OK to hardcode? config["class"]
        rvg_params = s2c.get_class_with_defaults("ReportVectorStats", manifest.schema_file)
        rvg_params = config_builder(rvg_params)
        rvg_params.finalize()
        rvg_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(rvg_params))


@dataclass
class MalariaSummaryReport(BuiltInReporter):
    """
        The population-level malaria summary report is a JSON-formatted report (MalariaSummaryReport.json) that provides
        a summary of malaria data across the population. The data are grouped into different bins such as age,
        parasitemia, and infectiousness.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaSummaryReport"
        report_params = s2c.get_class_with_defaults("MalariaSummaryReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class MalariaPatientJSONReport(BuiltInReporter):
    """
        The malaria patient data report is a JSON-formatted report (MalariaPatientReport.json) that provides medical
        data for each individual on each day of the simulation. For example, for a specified number of time steps,
        each “patient” has information collected on the temperature of their fever, their parasite counts, treatments
        they received, and other relevant data.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaPatientJSONReport"
        report_params = s2c.get_class_with_defaults("MalariaPatientJSONReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportSimpleMalariaTransmissionJSON(BuiltInReporter):
    """
        The simple malaria transmission report (ReportSimpleMalariaTransmissionJSON.json) is a JSON-formatted report that
        provides data on malaria transmission, by tracking who transmitted malaria to whom.  The report can only be used
        when the simulation setup parameter **Malaria_Model** is set to MALARIA_MECHANISTIC_MODEL_WITH_CO_TRANSMISSION.
        This report is typically used as input to the GenEpi model.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportSimpleMalariaTransmissionJSON"
        report_params = s2c.get_class_with_defaults("ReportSimpleMalariaTransmissionJSON", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportMalariaFiltered(BuiltInReporter):
    """
        The malaria filtered report (ReportMalariaFiltered.json) is the same as the default InsetChart report, but
        provides filtering options to enable the user to select the data to be displayed for each time step or for
        each node. See InsetChart for more information about InsetChart.json.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportMalariaFiltered"
        report_params = s2c.get_class_with_defaults("ReportMalariaFiltered", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class SpatialReportMalariaFiltered(BuiltInReporter):
    """
        The filtered malaria spatial report (SpatialReportMalariaFiltered.bin) provides spatial information on malaria
        simulations and allows for filtering the data and collection over different intervals. This report is similar to
        the Spatial output report but allows for data collection and filtering over different intervals using the
        Start_Day and a Reporting_Interval parameters
    """

    def config(self, config_builder, manifest):
        self.class_name = "SpatialReportMalariaFiltered"
        report_params = s2c.get_class_with_defaults("SpatialReportMalariaFiltered", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")  # maybe that should be in finalize
        self.parameters.update(dict(report_params))


@dataclass
class ReportEventCounter(BuiltInReporter):
    """
        The event counter report is a JSON-formatted file (ReportEventCounter.json) that keeps track of how many of
        each event types occurs during a time step. The report produced is similar to the InsetChart.json channel
        report, where there is one channel for each event defined in the configuration file (config.json).
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportEventCounter"
        report_params = s2c.get_class_with_defaults("ReportEventCounter", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class MalariaSqlReport(BuiltInReporter):
    """
        The MalariaSQL report outputs epidemiological and transmission data. Because of the quantity and complexity of
        the data, the report output is a multi-table SQLite relational database (see https://sqlitebrowser.org/).
        Use the configuration parameters to manage the size of the database.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaSqlReport"
        report_params = s2c.get_class_with_defaults("MalariaSqlReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class VectorHabitatReport(BuiltInReporter):
    """
        The vector habitat report is a JSON-formatted file (VectorHabitatReport.json) containing habitat data for each
        vector species included in the simulation. It focuses on statistics relevant to mosquito developmental stages
        (e.g. eggs and larvae), such as egg capacity and larval crowding.
    """

    def config(self, config_builder, manifest):
        self.class_name = "VectorHabitatReport"
        report_params = s2c.get_class_with_defaults("VectorHabitatReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class MalariaImmunityReport(BuiltInReporter):
    """
        The malaria immunity report is a JSON-formatted file (MalariaImmunityReport.json) that provides statistics for
        several antibody types for specified age bins over a specified reporting duration. Specifically, the report
        tracks the average and standard deviation in the fraction of observed antibodies for merozoite surface protein (
        MSP), Plasmodium falciparum erythrocyte membrane protein 1 (PfEMP1), and non-specific (and less immunogenic)
        minor surface epitopes.  The total possible is determined by parameters Falciparum_MSP_Variants,
        Falciparum_PfEMP1_Variants, and Falciparum_Nonspecific_Types.  The greater the fraction, the more antibodies the
        individual has against possible new infections.  The smaller the fraction, the more naïve the individual’s
        immune system is to malaria.
    """

    def config(self, config_builder, manifest):
        self.class_name = "MalariaImmunityReport"
        report_params = s2c.get_class_with_defaults("MalariaImmunityReport", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class MalariaSurveyJSONAnalyzer(BuiltInReporter):
    def config(self, config_builder, manifest):
        self.class_name = "MalariaSurveyJSONAnalyzer"
        report_params = s2c.get_class_with_defaults("MalariaSurveyJSONAnalyzer", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportDrugStatus(BuiltInReporter):
    """
        The drug status report provides status information on the drugs that an individual has taken or is waiting to
        take. Because the report provides information for each drug, for each individual, and for each time step, you
        may want to use the Start_Day and End_Day parameters to limit the size the output file.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportDrugStatus"
        report_params = s2c.get_class_with_defaults("ReportDrugStatus", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportHumanMigrationTracking(BuiltInReporter):
    """
        The human migration tracking report is a CSV-formatted report (ReportHumanMigrationTracking.csv) that provides
        details about human travel during simulations. The report provides one line for each surviving individual who
        migrates during the simulation.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportHumanMigrationTracking"
        report_params = s2c.get_class_with_defaults("ReportHumanMigrationTracking", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportNodeDemographics(BuiltInReporter):
    """
        The node demographics report is a CSV-formatted report (ReportNodeDemographics.csv) that provides population
        information stratified by node. For each time step, the report collects data on each node and age bin.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportNodeDemographics"
        report_params = s2c.get_class_with_defaults("ReportNodeDemographics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportNodeDemographicsMalaria(BuiltInReporter):
    """
    This report extends the data collected in the ReportNodeDemographics by adding data about the number of
    infections with specific barcodes. The malaria node demographics genetics report does not include columns for
    Genome_Markers because this report assumes that the simulation setup parameter Malaria_Model is set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

    Note: If you need detailed data on the infections with different barcodes, use the MalariaSqlReport. That report
    contains data on all barcodes, without specifying what they are.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportNodeDemographicsMalaria"
        report_params = s2c.get_class_with_defaults("ReportNodeDemographicsMalaria", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportNodeDemographicsMalariaGenetics(BuiltInReporter):
    """
    This report extends the data collected in the ReportNodeDemographics by adding data about the number of
    infections with specific barcodes. The malaria node demographics genetics report does not include columns for
    Genome_Markers because this report assumes that the simulation setup parameter Malaria_Model is set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.

    Note: If you need detailed data on the infections with different barcodes, use the MalariaSqlReport. That report
    contains data on all barcodes, without specifying what they are.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportNodeDemographicsMalariaGenetics"
        report_params = s2c.get_class_with_defaults("ReportNodeDemographicsMalariaGenetics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportVectorMigration(BuiltInReporter):
    """
        This report provides detailed information on where and when vectors are migrating.  Because there can be one
        line for each migrating vector, you may want to use the Start_Day and End_Day parameters to limit the
        size the output file.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorMigration"
        report_params = s2c.get_class_with_defaults("ReportVectorMigration", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportVectorStatsMalariaGenetics(BuiltInReporter):
    """
    This report extends the data collected in the ReportVectorStats by adding data about the number of
    infections with specific barcodes. The malaria node demographics genetics report does not include columns for
    Genome_Markers because this report assumes that the simulation setup parameter Malaria_Model is set to
    MALARIA_MECHANISTIC_MODEL_WITH_PARASITE_GENETICS.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportVectorStatsMalariaGenetics"
        report_params = s2c.get_class_with_defaults("ReportVectorStatsMalariaGenetics", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))


@dataclass
class ReportInterventionPopAvg(BuiltInReporter):
    """
    ReportInterventionPopAvg is a CSV-formatted report that gives population average
    data on the usage of interventions.  It provides data on the fraction of people
    or nodes that have an intervention as well as averages on the intervention's efficacy.
    For each persistent intervention that has been distributed to a node or person,
    the report provides one line in the CSV for each intervention used in that node.
    Since node-level intervention (usually vector control) can only have one per node,
    the data will be for that one intervention.  The individual-level interventions
    will have data for the people in that node.
    """

    def config(self, config_builder, manifest):
        self.class_name = "ReportInterventionPopAvg"
        report_params = s2c.get_class_with_defaults("ReportInterventionPopAvg", manifest.schema_file)
        report_params = config_builder(report_params)
        report_params.finalize()
        report_params.pop("Sim_Types")
        self.parameters.update(dict(report_params))