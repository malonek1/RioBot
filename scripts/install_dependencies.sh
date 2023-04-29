echo "Installing dependencies for RioBot"

# Installing Python3 manually to get 3.11 instead of 3.7
# yum install -y python3, python3-pip
yum install -y gcc openssl-devel bzip2-devel libffi-devel

cd /opt
wget https://www.python.org/ftp/python/3.11.3/Python-3.11.3.tgz
tar xzf Python-3.11.3.tgz

cd Python-3.11.3
./configure --enable-optimizations
make altinstall

rm -f /opt/Python-3.11.3.tgz

/usr/local/bin/python3.9 -m pip install --upgrade pip
/usr/local/bin/pip3.9 install -U discord.py==2.1.0 glicko2==2.0.0 gspread==5.7.1 oauth2client==4.1.3 Pillow==9.4.0 python-dotenv==0.21.0 pytz==2022.7 requests==2.28.1
