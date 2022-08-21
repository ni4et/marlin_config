#!/usr/bin/python3

"""
 Program to port local changes to Marlin config files (DHT 2/2022)
 Note: I will automate after the second or third time so here we are.

 Goals:
 Handle the case where a define needs a diffrent value.
 where a //define needs to change to just #define.
 where a #define needs to be commented out.
 Make sure that the changes the are obvious in the modified file.
 Do this in a non-destructive way. The original files can be simply recovered.
 Allow for multiple passes with no effects from previous passes.
"""

""" Add the following to .vscode/tasks.json:
{
    // See https://go.microsoft.com/fwlink/?LinkId=733558
    // for the documentation about the tasks.json format
    "version": "2.0.0",
    "tasks": [
        {
            "label": "customize",
            "type": "shell",
            "command": "python3",
            "args": ["C:/Work/FLSUN-Marlin/marlin_config/marlin_config.py",
                "${workspaceRoot}/Marlin"]


        }
    ]
}
"""



import os
import sys
import locale
from operator import mod
from numpy import rec
from sympy import re
import tempfile as txf
import locale

#print(os.environ["PYTHONIOENCODING"])



# Where is our wishlist:
# To reset all the changes and recover the original files set this to None
# or pass an empty file.
#dictFile=None
dictFileName='configuration.txt' # in same directory as where the script runs 
# The change dictionary file is in the same dir as this python script.
dictFile=os.path.join(os.path.dirname(sys.argv[0]),dictFileName)


# the files in the working directory:
# Where is the marlin working directory from here:
dWork=sys.argv[1] # Passed as an argument from tasks.json
configPost='configuration_adv.h'
configPre='configuration.h'

featureRE='(^\s*//)?\s*#define\s+(\w+)' # Recognizes #defines with or without comment out

# The following strings sign our changes.  
# Vanity strings allowed here.
insrtStr='//+DHT' # Addded by tool.
coutStr='//-DHT' # Unconditionally comment out




# Marlin config file customizer.

# Input file 1 is the config file from the marlinfw github.
# Input file 2 is a file contiaining the defines that need to be changed/set/or commented out.

# Input file 1 requires no changes.  After being filtered by this program certain character sequences will be added around 
# changes and will be ignored if the file is again used as file 1. These signatures are desined to visibily identify changed
# lines.  
# In the output a line starting with '/*@*/' has been inserted by the tool.
# Lines begining with '//@' have been comented out by the tool.
# In this way the orignal contents can be inspected or restored if need be.
#
# Input file 2 contains #defines to replace/insert in file 1.  The entire line is inserted after the
# signature prefix so if the intention is to comment out something then that can be accpmplished by prefixing
# the line in file 2 with '//'.
# If a comment is needed in file 2 then prefix the line with an '@' in column 1.

import re


T=re.compile(featureRE)
D={} # The dictionary

def loadDictionary(dictFile):
    if dictFile!=None:
        with open(dictFile,encoding='utf-8') as file2:
            print("Reading wish list in: "+dictFile+".txt\n")
            for line2  in file2:
                line2=line2.strip()
                M2=T.match(line2) # Look for the #define
                if M2:
                    if ( M2[2] in D): # Duplicate
                        print("Duplicate key: "+line2);

                    D[M2[2]]=line2
    print("Done reading the change file ({}), substitutions availble: ".format(dictFile,D.__len__()))
#    print(k,D[k])
#
def translateFile(inFile):
    added=0
    deleted=0
    modified=0
    recovered=0

    #with open(inFile) as file1, txf.TemporaryFile() as file3:
    file3=txf.TemporaryFile(mode='w+',encoding='utf-8')
    # While reading the file ignore codec errors.
    with open(inFile,encoding='utf-8') as file1:  #, open(inFile,'w') as file3:
        for line1 in file1:
            line1=line1.strip()
            # Here, we repair the original file contents
            # //@ prefixes any line that we commented out. - strip the prefix
            # /*@*/ prefixes any line that we inserted just delete
            if line1.startswith(coutStr): # The line that was replaced from the previous run.
                line1=line1[len(coutStr):]
                recovered+=1
            if insrtStr in line1: #  The replacement line from the previous run.
                line1="" 
                deleted+=1
                continue

        # what passes this point should be the orignal file.
        

            M1=T.match(line1) # Look for the #define
            # At this point the match has looked for a '//' at the front of the line.
            # M[0] is the whole string
            # M[1] will hold the comment delimiter if there is one, ie: '//'
            # M[2] is the token
        
            if M1: # IOW a #define was found on the line
                M1comment=M1[1]!=None  # It was already commmented out.
                # look in the database:
                if (M1[2] in D): # This is a line we need to do something with
                    line2=D.pop(M1[2]) # Look it up. - Line 2 is the replacement.
                    M2=T.match(line2) # Check the replacement type
                    # If M2[1] is None then live replacement, else comment
                    M2comment=M2[1]!=None # IOW the replacement is a comment

                    # 4 possible cases:
                    #   M1          M2
                    #   comment -> comment  (// copy line out no change
                    #   comment -> #def    (  //old in //@// old  and /*@*/#def new out)
                    #   #def-> #def (changed) ( old in //@old and /*@*/#def new
                    #   #def-> comment      ( old in //@old out
                    # In all cases leave the original line, possiblly commented out
                    # coutStr may prefix line 1 (original)
                    # insrtStr always prefixes line 2 the replacement.
                    # Never modify a line already commented out.
                    if M1comment and M2comment: # Dont do anything
                        # Both were comments.0
                        print(line1,file=file3) # Pass on the original line.
                    elif M1comment and not M2comment:
                        print(line1,file=file3)  # Always the line commented out.
                        print(line2+' '+insrtStr+' ',file=file3) # always the line added.
                        added+=1

                    elif not M1comment and not M2comment:
                        print(coutStr+line1,file=file3)  # Always the line commented out.
                        modified+=1
                        print(line2+' '+insrtStr+' ',file=file3) # always the line added.
                        added+=1

                    else: # not M1 & M2
                        print(coutStr+line1,file=file3)  # Always the line commented out.
                        modified+=1
                        # The line we would have put back is also a comment we dont need to add another.
                        
                        
                    
                else: # Pass unchanged - we dont know the token
                    print(line1,file=file3)
            else: # The line is not a #define
                print(line1,file=file3) # Goes out unchanged
    
    print('Done reading files ({}):'.format(inFile))
    

    file3.seek(0) # rewind the output

    with open(inFile,'w',encoding='utf-8') as file4:
        print('Copying:')
        while True:
            rb=file3.read()
            if rb=='':
                break
            file4.write(rb)

    print('Done with copy. modified={}, added={}, deleted={},recovered={}'.format(modified,added,deleted, recovered))
    # temporary file3 goes out of scope here.

def finish(inFile):
    """
    Open a temporary file, write the leftovers to it and then open the 
    infile to read and copy to the tmp copy.
    Then copy the tmp file to the infile.
    """

    # Dump anything remaining in the dictionary at the end 

    if D.__len__()>0:
        with open(inFile,'a',encoding='utf-8') as fileS: # Copy remaining records to infile
            print('APPENDING {} records to {}'.format(D.__len__(),inFile))
            print('CHECK THE FILE!\n\n')
            print(insrtStr,file=fileS)
            print(insrtStr+"// The following defines in the template didn't get used.",file=fileS)
            print(insrtStr,file=fileS)
            for line4 in D:
                print(D[line4]+insrtStr,file=fileS) # always the line added.
            print(insrtStr,file=fileS)
            print(insrtStr,file=fileS) 




def main():
    loadDictionary(dictFile)
    # In and out files can be the same:
    translateFile(os.path.join(dWork,configPre))
    translateFile(os.path.join(dWork,configPost))
    finish(os.path.join(dWork,configPre))

if __name__ == "__main__":
    main()
