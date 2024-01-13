# Define server details
$SERVER_USER = "bashir-ssh"
$SERVER_HOST = "154.56.60.12"
$SERVER_PATH = "/home/langora/htdocs/www.langora.online/"

# SSH into the server and run commands
$SSHCommand = @"
    # Navigate to the server path
    cd $SERVER_PATH

    # Check if the directory exists
    if [ -d "src" ]; then
        # Directory exists, pull latest changes
        git pull origin main
    else
        # Directory does not exist, clone the Git repository
        git clone https://github.com/bashirmanafikhi/BinanceTradingBot.git .

        # Create a virtual environment (assuming Python3 is installed)
        python3 -m venv venv
    fi
    
    # Activate the virtual environment
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt

    # Run any database migrations if needed
    # flask db upgrade

    cd src

    # Start Gunicorn in the background
    gunicorn -w 4 -b 0.0.0.0:5000 app:app -D
"@

# Run SSH command
ssh -i "~/.ssh/id_rsa" "$SERVER_USER@$SERVER_HOST" $SSHCommand
