
echo "Test #1: Simple put and get"

EXPECTED=" asdfasdfasdfasdf"

python client.py put -n "b.txt" -d "asdfasdfasdfasdf"

OUTPUT=$(python client.py get -n "b.txt" --t)

echo $OUTPUT

PARSED=$(echo $OUTPUT | cut -d: -f3)

echo "PARSED:" $PARSED

if [ "$EXPECTED" != "$PARSED" ]
then
echo "Not equal, get failed"
else
echo "They are equal"
fi

#---------------------------------------------------

echo "Test #2: Write to an already existing file"

EXPECTED2="asdfasdfasdfasdf;lkj;lkj;lkj;lkj"

python client.py put -n "rare.txt" -d ";lkj;lkj;lkj;lkj"

OUTPUT2=$(python client.py get -n "rare.txt" --t)

if [ "$OUPUT2" != "$EXPECTED2" ] 
then
echo "Not equal, get failed"
fi

#---------------------------------------------------

echo "Test #3: Try to read file without cap"

python client.py put -n "poiu.txt" -d "asdfasdf"

OUTPUT=$(python client.py get -n "poiu.txt" --t)

echo $OUTPUT

#switch users

sudo su Tito <<EOF

python client.py get -n "poiu.txt"

EOF

#echo $read

#echo $OUTPUT | cut -d: -f3

#if [ "$read" == "$

#exit

#echo $read
#---------------------------------------------------

echo "Test #4: Make sure people with corrent capabilites can access"




#--------------------------------------------------

echo "Test #5: File has been modified"

fileInfo=$(python client.py put -n "mod.txt" -d "asdfasdf")

echo $fileInfo

wc="$(echo $fileInfo | cut -dR -f1 | cut -ds -f2)"

echo $wc

python client.py put -wc $wc -d ";lkj;lkj"

newFile=$(python client.py get -n "mod.txt" --t)

echo $newFile

if [ "$getInfo" == "$newFile" ] 
then
echo "Success"
fi

