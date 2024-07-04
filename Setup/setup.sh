#!/bin/bash

uname
root=$(pwd)

# Determine the user's home directory dynamically
USER_HOME=$(eval echo ~${SUDO_USER})

# Add the user's .local/bin directory to PATH
export PATH=$PATH:$USER_HOME/.local/bin

# check if linux or macos
if [ $(uname) = 'Linux' ]
    then
        echo "Linux"
        which apt
        if [ $? -eq 0 ]
            then
                echo "apt found"
                sudo apt-get update
                sudo apt-get install apache2-dev apache2
                sudo apt install python3 python3-dev virtualenv
                sudo apt-get install libssl-dev openssl
                which python3.10
                if [ $? eq 0 ]
                    then
                	echo "python3.10 found"
                    else
                    	echo "installing python 3.10"
                    	wget https://www.python.org/ftp/python/3.10.14/Python-3.10.14.tgz
                	tar -xf Python-3.10.14.tgz
                	cd Python-3.10.14
                	./configure --enable-optimizations
                	make -j $(nproc)
                	sudo make altinstall
                fi
                cd $root"/Source"
                virtualenv --python=python3.10 vsenv
                source vsenv/bin/activate
                python3.10 -m pip install -r requirements.txt
                mod_wsgi-express start-server wsgi.py --port=80 --user daemon --group daemon --server-root=$root"/Server"
        else
            echo "apt not found"
        fi

    else
        echo "MacOS"
fi
