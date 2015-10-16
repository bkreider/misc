#!/bin/bash

echo "called like this:  $*"

NO_ARGS=0 
E_OPTERROR=85

if [ $# -eq "$NO_ARGS" ]    # Script invoked with no command-line args?
then
  echo "Usage: `basename $0` options (-w)"
  exit $E_OPTERROR          # Exit and explain usage.
fi  

while getopts ":w:" Option
do
  case $Option in
    w     ) echo " Found argument \"$OPTARG\"   [OPTIND=${OPTIND}]";;
    *     ) echo "Unimplemented option chosen.";;   # Default.
  esac
done

shift $(($OPTIND - 1))



