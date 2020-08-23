#!/usr/bin/env python3
from pathlib import Path
import sys
from datetime import date
import subprocess as sp
import os
import boto3
import json


def new_search():
    """
    This method searches for new nexteq runs. Input is the nextseq absolute path, path for aws credentials, and name of docker container that contains demuxing scripts. 
    Searches for 2 things in order to start demux process:
        1) No Demux_log.txt
        2) RunCompletionStatus.xml
    """
    nextseq = Path(sys.argv[1])
    aws_creds = Path(sys.argv[2])
    dock = sys.argv[3]
    dirs = nextseq.glob('*')
    file_1 = "Demux_log.txt"
    file_2 = "RunCompletionStatus.xml" # File that marks sequencing run is complete #

    for folder in dirs:
        demux_log = folder/file_1
        complete_stat = folder/file_2
        today = date.today()
        if folder.is_dir():
            print(folder)
            if not demux_log.exists(): 
                if complete_stat.exists():
                    with open(f"{nextseq}/RUN_log","a") as run_log:
                        run_log.write(f"New Run:{folder},{today}\n")
                    print("NEW RUN - performing DEMUX. mamba out.")
                    os.chdir(folder)
                    run_dir = folder.name
                    with open(f"{nextseq}/Demux_log.txt","w+") as demux_log:                    
                    """
                    A text file logging the date and time of finding a new nextseq sequencing run from an Illumina Nextseq machine is written in the directory where the directory that the data is being uploaded to. 
                    Once a new run is found and its sequencing is complete, a docker run commmand is performed. The container has all scripts required for demuxing data. 
                    """ 
                        demux_log.write(f"{folder},{today}")
                    docker_run = f"docker run -v {aws_creds}:/root/.aws -v {folder}:/home/{run_dir} {dock} {folder}"

                    print(docker_run) # print cmd 
                    sp.run(docker_run) # to run command 
                else:
                    print("Demux Run NOT COMPLETE. Try again later. sorry.")
            else:
                print("OLD RUN - Exiting. peace.")


if __name__ == "__main__":
    try:
        new_search()
        print("Run directory search complete")
    except Exception as e:
        print(e)

