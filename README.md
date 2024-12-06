# baseball

## Installation Instructions

### Prerequisities
1. Install Anaconda Distribution
2. Install PostgreSQL Server (on this machine or a shared server)
3. Install PostgreSQL Client Tools

### Install on a Mac
1. Open a new terminal window
2. conda create -n baseball
3. conda activate baseball
4. conda install python=3.11
5. make install
6. Change config values and db name in Makefile
7. make db


Setup instructions for Mac M1
brew install freetds


"Driver={/opt/homebrew/lib/libmsodbcsql.18.dylib};" \
                        f"Server={db_server};" \
                        f"Database={db_database};" \
                        f"uid={db_user};" \
                        f"pwd={db_password};" \
                        "Trusted_Connection=no;"

Field Positions Reference:
https://en.wikipedia.org/wiki/Baseball_positions

Play by Play Data File Formats:
https://www.retrosheet.org/game.htm
