"""
A home-made function to import data from CQuest result files : *_quest2.txt by Gael Villa
"""
import warnings

import numpy as np
import pandas as pd


def get_quest2(quest2_path, verbose=False) -> pd.DataFrame:
    """ A home-made function to import data from CQuest result files : *_quest2.txt"""

    class LineInfo:
        """A finite state machine to control each step while reading the result file."""

        def __init__(self):
            self.state = "Newline"
            self.index = 0

        def refresh(self, input_data) -> None:
            """Update the state based on the input data."""
            self.index += 1
            if not input_data:  # Current line is empty
                # Case : Expected New line --> Nothing to do
                if self.state in ["Newline", "Record", "Warning"]:
                    self.state = "Newline"
                # Case : End of metabolite block --> Record metabolite data
                elif self.state == "Values":
                    self.state = "Record"
                # Case : Unexpected New Line --> Error State
                else:
                    self.state = "Error"
            # Case : Metabolite name
            elif input_data == 'Metabolite:' and self.state == "Newline":
                self.state = "Metabolite"
            # Case : Parameter names
            elif input_data.split()[0].isalpha() and self.state == "Metabolite":
                self.state = "Parameters"
            # Case : Parameter values
            elif input_data.isnumeric() and self.state == "Parameters":
                self.state = "Values"
            # Case : Warning message (seen on several files)
            elif input_data.split()[0] == 'WARNING!' and self.state == "Newline":
                self.state = "Warning"
            # Case : Unexpected 1st word --> Error state
            else:
                self.state = "Error"

        def get_state(self) -> str:
            """Return the current state of the finite state machine."""
            return self.state

    # Main program
    # Create an empty data frame
    data = pd.DataFrame()
    # Read the result file
    with open(quest2_path, 'r', encoding='utf-8') as f:
        # Initiate the finite state machine to control each line of the result file
        line_info = LineInfo()
        # Read each line
        for line in f:
            # Split the line and read 1st word
            words = line[:-1].split('\t')
            # Update the line state according to the 1st word
            line_info.refresh(words[0])
            # Case : Metabolite name
            if line_info.state == 'Metabolite':
                # Create new frame for this metabolite
                frame = {
                    "Metabolite": words[1].split("_")[0]  # Short name
                }
                params = []
                values = []
            # Case : Parameter names
            elif line_info.state == "Parameters":
                # List of parameters, excluding "Pixel Position"
                params = ['_'.join(param_str.split(' ')) for param_str in words[1:] if param_str]
            # Case : Parameter values
            elif line_info.state == "Values":
                # List of parameter values, excluding Pixel & Position
                values = [val_str for val_str in words[2:] if val_str]
            # Case : Record parameter values after metabolite block
            elif line_info.state == "Record":
                # Update the frame
                frame.update(dict(zip(params, values)))
                # Add line_info frame to the data
                data = pd.concat([data, pd.DataFrame([frame])], ignore_index=True)
            # Case : Warning
            elif line_info.state == 'Warning':
                # Display warning message
                if verbose:
                    warnings.warn(f"In Quest File: {quest2_path}\nIn line N°{line_info.index}: {line[:-1]}'\n")

            # Case : Error state
            elif line_info.state == 'Error':
                raise ValueError(f"Error while importing Quest results!\n"
                                 f"File: {quest2_path}\n"
                                 f"In line N°{line_info.index}: '{line[:-1]}'.\n"
                                 f"Check data format.")

            else:  # Case : New line
                # Nothing to do
                pass
    # Return
    return data


def get_lcmodel(table_path) -> tuple[pd.DataFrame, list]:
    """Function to read a .table file after LCmodel execution"""

    # Create an empty data frame
    data = pd.DataFrame()

    # Read the result file
    with open(table_path, 'r') as f:
        # Look for Concentration data
        while f.readline().split(' ')[0] != "$$CONC":
            pass
        # Get headers
        line = f.readline()[:-1]
        headers = list(filter(None, line.split()))
        lh = len(headers)
        # Get the data
        rawdata = []
        line = f.readline()[:-1]
        while line:
            # Split line by unknown number of spaces
            l = list(filter(None, line.split()))
            if len(l) < lh:
                # Problem when a +/- sign replaces the space for macromolecules
                for sep in ["+", "-"]:
                    if sep in l[-1]:
                        l = l[:-1] + l[-1].split(sep)
                        # Update the result matrix
            rawdata.append(l)
            # Read new line
            line = f.readline()[:-1]
        # Look for the Diagnostics table
        while f.readline().split(' ')[0] != "$$DIAG":
            pass
        # Read first line after $$DIAG
        line = f.readline()[:-1]
        diag = []
        # Record each line
        while line:
            diag.append(line)
            line = f.readline()[:-1]

    # Convert the data to a dataframe
    data = pd.DataFrame(
        {
            headers[j]: [
                rawdata[i][j] for i in range(len(rawdata))
            ] for j in range(len(headers))
        }
    )
    # Return the results
    return data, diag


def parse_lcmodel(data_raw, diag) -> pd.DataFrame:
    """Function that converts string outputs from LCModel outputs to
    the correct format. For LCmodel, the diagnosis variable is a list of strings"""

    # Convert the raw data
    data_exec = pd.DataFrame(
        {
            "Metabolite": data_raw["Metabolite"],
            "Rate_Raw": data_raw["Conc."].astype(float),
            "Rate_Cr": data_raw["/Cr+PCr"].astype(float),
        }
    )
    data_exec["CRLB_Raw"] = data_raw["%SD"].str.rstrip("%").astype(float) * data_exec["Rate_Raw"] / 100

    # Add groups of metabolites
    meta_groups = [
        # ("PCho", "GPC", "MM32"),
        # ("NAA", "NAAG", "MM20"),
    ]
    if meta_groups:
        # New frames to add
        data_exec.set_index(data_exec["Metabolite"], inplace=True)
        new_frames = pd.DataFrame(
            {
                "Metabolite": [
                    "+".join([meta for meta in group])
                    for group in meta_groups
                ],
                "Rate_Raw": [
                    np.sum([data_exec["Rate_Raw"][meta] for meta in group])
                    for group in meta_groups
                ]
            },
            index=meta_groups
        )
        # Concatenate
        data_exec = pd.concat([data_exec, new_frames]).reset_index(drop=True)

    # Apply convergence criteria to the fit diagnosis
    # 1: LCModel returns Zero concentration rates and 999% CRB when it fails to fit
    true_fit = float(data_exec.query("Metabolite == 'Cr+PCr'")["Rate_Cr"].iloc[0]) != 0
    # 2: from $$DIAG able. See LCmodel manual p.154 $12.2 : "Standard Diagnotics"
    for d in diag:
        true_fit = true_fit \
                   and (list(filter(None, d.split()))[1] in ["info", "info's", "warning"])

    # Return the dataframe with convergence diagnosis
    return data_exec.assign(Convergence=true_fit)
