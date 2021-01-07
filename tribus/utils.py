'''help validate inputs for main'''
from . import classify

def runClassify(args):
    print(args.input)
    print(args.labels)
    # create output folder
    # check channel names
    # check label logic
    # count all requirements present
    # levels of calls
    # parse the table into a better structure, list? array? dict?
    result = classify.run(input,labels)
    
    # write CSVs
    return(args.input,args.labels)



# future: check output folder for existing labels, have they changed? which ones changed?