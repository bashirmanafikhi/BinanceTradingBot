# Define server details
$SERVER_USER = "bashir-ssh"
$SERVER_HOST = "154.56.60.12"
$SERVER_PATH = "/home/langora/htdocs/www.langora.online/"

# SSH into the server and run commands
$SSHCommand = @"
    # Navigate to the server path
    cd $SERVER_PATH

    # Clone your Git repository (replace with your repository URL)
    git clone https://github.com/bashirmanafikhi/BinanceTradingBot.git .

    # Create a virtual environment (assuming Python3 is installed)
    python3 -m venv venv
    
    # Activate the virtual environment
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt

    # Navigate to the 'src' folder
    cd src

    # Run any database migrations if needed
    # flask db upgrade

    # Start Gunicorn in the background
    gunicorn -w 4 -b 0.0.0.0:5000 app:app -D
"@

# Run SSH command
ssh -i "~/.ssh/id_rsa" "$SERVER_USER@$SERVER_HOST" $SSHCommand
