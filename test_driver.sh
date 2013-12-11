
echo "Test #1: Simple put and get"

EXPECTED=" asdfasdfasdfasdf"

python client.py put -n "b.txt" -d "asdfasdfasdfasdf"

OUTPUT=$(python client.py get -n "b.txt")

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

OUTPUT2=$(python client.py get -n "rare.txt")

if [ "$OUPUT2" != "$EXPECTED2" ] 
then
echo "Not equal, get failed"
fi

#---------------------------------------------------

echo "Test #3: Write to file of which I do not have access"



#---------------------------------------------------

echo "Test #4: Make sure people with corrent capabilites can access"




#--------------------------------------------------

echo "Test #5: File has been modified"