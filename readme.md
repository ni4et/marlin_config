Simple tool to port Marlin customizations to new versions of Marlin.
Usage:
    Collect all desired configuration changes into one file, configuration.txt. Both configuration.h and configuration_adv.h will be scanned so you dont need to know which file holds any particular paramenter.
    Run the python script marlin_config.py with sys.arg[1] pointing to the target Marlin build tree, and the location of the target header files.
    Any unresolved defines will be written to the end of configuration.h. Inspect both files to assure the desired result.
    Build Marlin.

    Users of vscode can put the contents of tasks.json in the .vscode directory
    and use the task menu to help. Configure this file for your particular environment.

The syntax of configuration.txt is like this.
There is no required order, your changes will be placed in the target files where they belong.

Commment lines start with an '@' sign and will be ignored.:

    @ My customizations for my cube and octopus board.
    @ #define NOZZLE_TO_PROBE_OFFSET { 22, 0, 0 }

Lines that start with "#define" will replace the coresponding lines in the configuration files.

    #define AUTO_POWER_CONTROL      // Enable automatic control of the PS_ON pin

Lines that start with "//#define" will comment out the target line.

        //#define AUTO_POWER_FANS         //Not needed with OCTOPUS_V1_1 - Board powers fans.

The resulting config file will look like this:

        //#define AUTO_POWER_CONTROL      // Enable automatic control of the PS_ON pin
        #define AUTO_POWER_CONTROL      // Enable automatic control of the PS_ON pin //+DHT 
        //-DHT#define AUTO_POWER_FANS         // Turn on PSU if fans need power


The first line is the original line as is.

The second line is the replacement.

The third line is the original line, now commented out.

The special strings '//-DHT' and '//+DHT' are markers so that the changes we made can be found. Lines that contain either of these strings will be recovered to their orignal content before new changes are applied.

This should be almost like the files were modified manually with each change signed by the user.  It so happens that running the modified files against an >empty< configuration.txt will restore the cofiguration files to their original unconfigured state.

Yes, my initials are "DHT".  Change the 2 lines in the python file if you need to.  "DHT" is a string that doesn't show up much in code so grep won't be finding it extraneously.  
