# Define server details
$SERVER_USER = "root"
#$SERVER_USER = "bashir-ssh"
$SERVER_HOST = "154.56.60.12"
$SERVER_PATH = "/home/langora/htdocs/www.langora.online/"

# SSH into the server and run commands
$SSHCommand = @"

    # # Navigate to the server path
    # cd $SERVER_PATH

    # # go back to parent folder
    # cd ..

    # # Remove the www.langora.online folder and its subfolders
    # rm -rf www.langora.online

    # # Recreate the directory
    # mkdir www.langora.online


    # Navigate to the server path
    cd $SERVER_PATH

    # Check if the directory exists
    if [ -d "app" ]; then
        # discard local changes
        git restore .
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

    # set environment variable
    export FLASK_ENV=production

    # Install Python dependencies
    pip install -r requirements.txt

    cd app

    # Check if the process is running on port 5000
    # lsof -i :5000
    if lsof -t -i :5000 > /dev/null 2>&1; then
        # If running, find and kill the existing process
        lsof -t -i :5000 | xargs kill -9
    fi
    
    #uwsgi --http 0.0.0.0:5000 --http-websockets --master -p 4 -w run_web:app --enable-threads
    
    # Start Gunicorn in the background
    gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 run_web:app --log-level info --error-logfile log/gunicorn_error.log --capture-output -D
    #gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 run_web:app -D
"@

# Run SSH command
ssh -i "~/.ssh/id_rsa" "$SERVER_USER@$SERVER_HOST" "$SSHCommand"
