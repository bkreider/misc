#!/bin/bash

# Anaconda and miniconda are mutually exclusive anyway
installer_name="*-Linux-x86_64.sh"

installer_path=/var/lib/anaconda
install_dir=/opt/anaconda

/bin/bash ${installer_path}/${installer_name} -b -p ${install_dir}

