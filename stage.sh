#!/bin/bash
target=$1
execution_type=$2
file_count=$3 
echo

if [ $execution_type == "full" ]
then 
    echo "Running UPLOAD script. Target: $1 | File Step: $2"
    bash create.sh $1 upload $3
    echo "UPLOAD COMPLETE. waiting seconds to add edits"
    time_to_wait=$((2 * file_count)) 
    echo "waiting $time_to_wait seconds to edit files"
    sleep $time_to_wait
    echo
    echo "Running EDIT script. Target: $1 | File Step: $2"
    bash create.sh $1 edit $3
    echo "EDIT COMPLETE."

else
    echo "Running $execution_type script. Target: $1 | File Step: $2"
    bash create.sh $1 $2 $3
    echo "$execution COMPLETE."
fi

echo "Process complete. exiting..."