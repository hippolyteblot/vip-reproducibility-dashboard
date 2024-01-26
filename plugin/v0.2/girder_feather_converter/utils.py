import warnings
import pandas as pd


# Original function from Gael Villa
def get_quest2(quest2_path, verbose=False) -> pd.DataFrame:
    """ A home-made function to import data from CQuest result files : *_quest2.txt"""
    
    class __LineInfo():
        """A finite state machine to control each step while reading the result file"""

        def __init__(self):
            self.state = "Newline"
            self.index = 0

        def refresh(self, input) -> None:
            """input = first element of a new line (sep='\t') in the result file""" 
            self.index += 1
            if not input: # Current line is empty
                # Case : Expected New line --> Nothing to do
                if self.state in ["Newline", "Record", "Warning"] : 
                    self.state = "Newline"
                # Case : End of metabolite block --> Record metabolite data
                elif self.state == "Values" : 
                    self.state = "Record" 
                # Case : Unexpected New Line --> Error State
                else:
                    self.state = "Error"
            # Case : Metabolite name
            elif input == 'Metabolite:' and self.state == "Newline" : 
                self.state = "Metabolite"
            # Case : Parameter names
            elif input.split()[0].isalpha() and self.state == "Metabolite" : 
                self.state = "Parameters" 
            # Case : Parameter values
            elif input.isnumeric() and self.state == "Parameters" : 
                self.state = "Values" 
            # Case : Warning message (seen on several files)
            elif input.split()[0] == 'WARNING!' and self.state == "Newline" : 
                self.state = "Warning"
            # Case : Unexpected 1st word --> Error state
            else:
                self.state = "Error"

    # Main program 
    data = pd.DataFrame()
    with open('venv/storage/' + quest2_path, 'r') as f:
        print("opened")
        # Initiate the finite state machine to control each line of the result file
        line_info = __LineInfo()
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
                    "Metabolite": words[1].split("_")[0] # Short name
                }
                params = []
                values = []
            # Case : Parameter names
            elif line_info.state == "Parameters":
                # List of parameters, excluding "Pixel Position"
                params = [ '_'.join(param_str.split(' ')) for param_str in words[1:] if param_str ]
            # Case : Parameter values
            elif line_info.state == "Values":
                # List of parameter values, excluding Pixel & Position
                values = [ val_str for val_str in words[2:] if val_str ]
            # Case : Record parameter values after metabolite block
            elif line_info.state == "Record":
                # Update the frame
                frame.update( dict(zip(params, values)) )
                # Add line_info frame to the data
                data = pd.concat([ data, pd.DataFrame([frame]) ], ignore_index=True )
            # Case : Warning
            elif line_info.state == 'Warning' : 
                # Display warning message
                if verbose:
                    warnings.warn("In Quest File: {}\n\
                        In line N°{}: {}'\n".format(quest2_path, line_info.index, line[:-1]) )
            # Case : Error state
            elif line_info.state == 'Error': 
                raise Exception( "Error while importing Quest results !\n\
                    File: {}\n\t In line N°{}: '{}'.\n\
                    Check data format.".format(quest2_path, line_info.index, line[:-1]) )
            else: # Case : New line 
                # Nothing to to
                pass
    # Return
    return data