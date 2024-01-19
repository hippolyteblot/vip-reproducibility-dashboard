import os
import warnings
import pandas as pd




def get_quest2(quest2_path, verbose=False) -> tuple[pd.DataFrame, str]:
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
    # End of the finite state machine

    # Main program 
    # Create an empty data frame 
    data = pd.DataFrame()
    # Read the result file
    with open(quest2_path, 'r') as f:
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


def convert_to_feather(quest2_path, dir, verbose=False) -> None:
    # Get the data
    data = get_quest2(quest2_path, verbose=verbose)
    # Get only the file name from quest2_path
    file_name = os.path.basename(quest2_path)
    # Save the data
    print("Saving " + dir + "/" + file_name[:-11] + '.feather')
    data.to_feather(dir + "/" + file_name[:-11] + '.feather')


def invert_folders(path):
    times_list = []
    dataframes_list = []
    # for each file in this dir
    folders_list = os.listdir(path)
    for subfolder in folders_list:
        # add the name of the folder to the list
        for subsubfolder in os.listdir(path + '/' + subfolder):
            if subsubfolder not in times_list:
                times_list.append(subsubfolder)
                dataframes_list.append({
                    'Folder': subfolder,
                    'Time': subsubfolder,
                    'Data': pd.DataFrame()
                })
    
    for subfolder in folders_list:
        for time in times_list:
            # get the file ending with _quest2.txt
            if os.path.exists(path + '/' + subfolder + '/' + time):
                for file in os.listdir(path + '/' + subfolder + '/' + time):
                    if file.endswith('_quest2.txt'):
                        tmp_df = pd.read_feather(path + '/' + subfolder + '/' + time + '/' + file[:-11] + '.feather')
                        # add a column with the name of the folder
                        tmp_df['Folder'] = subfolder
                        # concatenate the dataframes
                        for df in dataframes_list:
                            if df['Time'] == time:
                                df['Data'] = pd.concat([df['Data'], tmp_df], ignore_index=True)
                                break
    # now save each dataframe as a feather file into a file named with the time at the source
    for df in dataframes_list:
        df['Data'].to_feather(path + '/' + df['Time'] + '.feather')
    return dataframes_list


print(invert_folders('data/B'))
