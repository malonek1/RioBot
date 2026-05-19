echo "Installing dependencies for RioBot"

if ! command -v python3.9 &> /dev/null; then
    echo "Python 3.9 not found, installing..."
    yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib

    cd /opt
    wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz
    tar xzf Python-3.9.6.tgz

    cd Python-3.9.6
    ./configure --enable-optimizations
    make altinstall

    rm -f /opt/Python-3.9.6.tgz
else
    echo "Python 3.9 already installed, skipping."
fi

/usr/local/bin/python3.9 -m pip install --upgrade pip
/usr/local/bin/pip3.9 install -r /home/ec2-user/RioBot/requirements.txt
