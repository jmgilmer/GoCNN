#!/bin/bash
val=0
count=0
for file in ./train/*; do
	if ! ((val % 100)); then
		mv "$file" ./test
		echo "$file"
		let "count+=1"
	fi
	let "val+=1"
done
echo "$count"