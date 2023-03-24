#!/bin/bash
target=$1
action=$2
file_count=$3


SBX_PATH=/Users/rduchin/Library/CloudStorage/Box-Box/fake_users_files
PATH=$PWD/fake_users_files
FILE_NAME="4generate-"
unique=$RANDOM
if [ $target == "sandbox" ]
then
    target_path=$SBX_PATH
elif [ $target == "local" ]
then
    target_path=$PATH
else
    echo "please supply target for file creation. Usage: ./create.sh <local|sandbox> <upload|edit|ransom|full> <# of files> "  
    exit 1
fi 

if [ $action == "upload" ]
then
    version_text="First Upload"
elif [ $action == "edit" ]
then
    version_text="FINAL VERSION BEFORE ATTACK Made an edit"

elif [ $action == "ransom" ]
then
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 ransomware_attack.py $target_path e test
else
    echo "please supply action. Usage: ./create.sh <local|sandbox> <upload|edit|ransom|full>  <# of files>"  
    exit 1
fi
for ((i=0; i<=$file_count; i++))
do
    echo $version_text This is unencrypted content YES! $unique> $target_path/"$FILE_NAME$i.txt"
done