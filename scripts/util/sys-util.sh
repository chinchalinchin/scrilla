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
                echo "$f"
                dos2unix "$f"
            fi
        fi
    done
}

function make_scripts_executable(){
    for f in $1/*
    do
        if [ -d $f ]
        then
            make_scripts_executable $f
        else
            if [ ${f: -3} == ".sh" ]
            then
                echo "$f"
                chmod u+x "$f"
            fi
        fi
    done
}

if [ "$1" == "unixify" ] || [ "$1" == "-u" ] || [ "$1" == "--u" ]
then
    unixify "$2"
elif [ "$1" == "execute" ] || [ "$1" == "-e" ] || [ "$1" == "--e" ]
then
    make_scripts_executable "$2"
fi