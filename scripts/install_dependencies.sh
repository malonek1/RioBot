echo "Installing dependencies for RioBot"

if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 not found, installing..."
    dnf install -y python3.11 python3.11-pip
else
    echo "Python 3.11 already installed, skipping."
fi

/usr/bin/python3.11 -m pip install --upgrade pip
/usr/bin/python3.11 -m pip install -r /home/ec2-user/RioBot/requirements.txt
