# Get rid of all those pesky \r errors!

function unixify(){
    for f in $1/*
    do
        if [ -d $f ]
        then 
            unixify $f
        else
            if [ ${f: -3} == ".sh" ]
            then
                dos2unix $f
            fi
        fi
    done
}

unixify $1