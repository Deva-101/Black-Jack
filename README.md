# Online Black Jack

**Online Black Jack** is a multiplayer card game built in Python, where players can connect over a local Wi-Fi network to enjoy a classic Black Jack experience. The game uses a client-server model, with `server.py` acting as the backend server and `client.py` serving as the standalone client for players.

## Recommended Screen Dimensions
- **Width**: 1920px
- **Height**: 1080px

## Features
- Multiplayer gameplay over the same Wi-Fi network
- Classic Black Jack rules with real-time updates
- Supports up to [X] players connected to the server

## Installation
To run this project locally:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Online-Black-Jack.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Online-Black-Jack
    ```
3. Ensure you have Python 3.x installed on your system.

4. Install any required Python packages (if applicable):
    ```bash
    pip install -r requirements.txt
    ```

5. Start the server:
    ```bash
    python server.py
    ```

6. On each client machine (players), run:
    ```bash
    python client.py
    ```

7. Make sure all players are connected to the same Wi-Fi network.

## Usage
- Run `server.py` on one machine to start the game server.
- Players on the same Wi-Fi network can run `client.py` to connect to the server and join the game.
- Follow the on-screen prompts to start playing Black Jack with your friends.

## Tech Stack
- **Language**: Python
- **Backend**: `server.py` handles game logic and manages connections.
- **Client**: `client.py` connects to the server for multiplayer functionality over the network.
- **Networking**: Socket programming in Python for real-time communication between the server and clients.

## Future Improvements
- Add support for online play over the internet (across different networks)
- Enhance the game interface for smaller screen sizes
- Introduce an AI dealer for single-player mode

## Contributions
Contributions are welcome! Feel free to submit issues or pull requests to improve the game.
