



import os


path = "repro-spectro-master-results-isbi-work-1-cquest/results/isbi-work-1/cquest"
out = "results-isbi-work-1-cquest"
os.mkdir(out)

experiments = os.listdir(path)
for experiment in experiments:
    signals = os.listdir(path + '/' + experiment)
    workflows = os.listdir(path + '/' + experiment + '/' + signals[0])
    # create a folder for the experiment
    os.mkdir(out + '/' + experiment)
    for workflow in workflows:
        os.mkdir(out + '/' + experiment + '/' + workflow)
        # for each signal, get the workflow folder and its files into the new workflow folder
        for signal in signals:
            os.system('cp ' + path + '/' + experiment + '/' + signal + '/' + workflow + '/* ' + out + '/' + experiment + '/' + workflow + '/')

