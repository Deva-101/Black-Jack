import socket
import threading
import time
import random

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
connections = []
users = ["people in room: "]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
coins = 1000
active_instances = 0
turn = 0
game_started = False
everyone_betted = False
cards = [x for x in range(1, 52)]
active_cards = []
value_of_card = [[1, 11], [1, 11], [1, 11], [1, 11], 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
add_amount_list = []

dealer_chosen_card_1 = random.choice(cards)
cards.remove(dealer_chosen_card_1)
dealer_chosen_card_2 = random.choice(cards)
cards.remove(dealer_chosen_card_2)
dealer_cards = [dealer_chosen_card_1, dealer_chosen_card_2]
out_string = ""

main = "!@#$%^&*() Main Menu !@#$%^&*()"
game = "!@#$%^&*() Game Screen !@#$%^&*()"


def add_cards(p_turn, value_card, active_card, dealer):
    ace = []
    number = 0
    outString = "card_numbers:"
    if dealer:
        outString = "dealer_card_numbers:"
        for card in active_card:
            outString += " " + str(card)
            if (card-1) < 4:
                ace.append(1)
            else:
                number += value_card[card-1]
    else:
        for card in active_card[p_turn]:
            outString += " " + str(card)
            if (card-1) < 4:
                ace.append(1)
            else:
                number += value_card[card-1]
    if ace:
        for x in range(len(ace)):
            if (11 + number) < 21:
                number += 11
            else:
                number += 1
    return number, outString


def recv(conn, addr):
    global connections, game_started, everyone_betted, cards, active_cards, dealer_cards, turn, out_string 
    while True:
        client_response = conn.recv(2048).decode(FORMAT)
        if "start_game" in client_response:
            game_started = True
            for con in connections[1:]:
                con.send("start_game".encode(FORMAT))
                time.sleep(0.25)
                
        elif "bet_amount" in client_response:
            client_response = client_response.split(" ")
            for count, connection in enumerate(connections):
                if connection == conn:
                    users[count + 1] += (f" (bet amount: {client_response[2]})")
        
        elif "hit" in client_response:
            chosen_card = random.choice(cards)
            cards.remove(chosen_card)
            active_cards[turn].append(chosen_card)
            
            add_number = 0
            ace = []
            out_string = "card_numbers:"
            
            for card in active_cards[turn]:
                out_string += " " + str(card)
                if (card-1) < 4:
                    ace.append(1)
                else:
                    add_number += value_of_card[card-1]
            if ace:
                for x in range(len(ace)):
                    if (11 + add_number) < 21:
                        add_number += 11
                    else:
                        add_number += 1
            if add_number > 21:
                conn.send(("bust: " + users[turn+1]).encode(FORMAT))
            add_amount_list[turn] = add_number
            time.sleep(0.5)
            if conn == connections[turn]:
                conn.send(out_string.encode(FORMAT))
            time.sleep(0.5)
            for con in connections:
                if con != connections[turn]:
                    con.send(f"user_num_of_cards: {users[turn+1]} {len(active_cards[turn])}".encode(FORMAT))
            time.sleep(0.5)


        elif "pass" in client_response:
            print("turn: " + str(turn))
            print("users: " + str(len(users)-2))
            
            if len(users)-2 > turn:
                turn += 1
            else:
                turn = 10  # 10 = dealer's turn
                
                dealer_add_number = 0
                while True:
                    dealer_add_number, out_string = add_cards(turn, value_of_card, dealer_cards, dealer=True)
                    print("DEALER TURN.......")
                    print(out_string)
                    time.sleep(0.5)
                    for con in connections:
                        con.send(out_string.encode(FORMAT))
                    time.sleep(0.5)
                    if dealer_add_number < 16:
                        dealer_chosen_card = random.choice(cards)
                        cards.remove(dealer_chosen_card)
                        dealer_cards.append(dealer_chosen_card)
                    elif dealer_add_number > 21:
                        conn.send(("bust: dealer").encode(FORMAT))
                        time.sleep(0.2)
                    else:
                        break
                    time.sleep(1.5)
                for counter, user_val in enumerate(add_amount_list):
                    if user_val > dealer_add_number and user_val < 22:
                        connections[counter].send("payout".encode(FORMAT))
                    else:
                        connections[counter].send("lost".encode(FORMAT))
                time.sleep(1.5)


def in_game(conn, addr):
    global active_instances, everyone_betted, game_started, dealer_chosen_card_2, add_amount_list
    once = True
    conn.send(game.encode(FORMAT))
    time.sleep(1)
    conn.send(("coins: " + str(coins)).encode(FORMAT))
    time.sleep(.5)

    thread = threading.Thread(target=recv, args=(conn, addr))
    thread.start()

    while True:
        if game_started and not everyone_betted:
            validate_list = []
            for user in users[1:]:
                if " (bet amount: " in user: 
                    validate_list.append("1")
            if len(validate_list) == (len(users) - 1):
                everyone_betted = True
                add_amount_list = [0 for x in range(len(users)-1)] 
        if everyone_betted:
            if once:
                conn.send((f"dealer_card: {dealer_chosen_card_2}").encode(FORMAT))
                chosen_card_1 = random.choice(cards)
                cards.remove(chosen_card_1)
                chosen_card_2 = random.choice(cards)
                cards.remove(chosen_card_2)
                time.sleep(0.5)
                active_cards.append([chosen_card_1, chosen_card_2])

                for x in range(len(active_cards)):
                    out_string = "card_numbers:"
                    for card in active_cards[x]:
                        out_string += " " + str(card)

                    connections[x].send(out_string.encode(FORMAT))
                
                once = False
            time.sleep(0.5)
            if int(turn+1) < int(len(users)): 
                conn.send(("player_turn: " + users[turn+1]).encode(FORMAT))
            else:
                conn.send("player_turn: dealer".encode(FORMAT))
            


        time.sleep(0.1)


        if connections:
            for counter, con in enumerate(connections):
                try:
                    con.send(str.encode("\n".join(users)))
                except:
                    con.close()
                    users.pop(counter + 1)
                    connections.pop(counter)
                    active_instances -= 1
        else:
            print("Everyone left the game...")
            active_instances = 0
            break
        time.sleep(.5)
        


def new_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")
    while True:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            username = conn.recv(msg_length).decode(FORMAT)
            users.append(username)
            break
    in_game(conn, addr)


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        global active_instances
        conn, addr = server.accept()
        if not game_started:
            if active_instances <= 4:
                connections.append(conn)
                thread = threading.Thread(target=new_client, args=(conn, addr))
                thread.start()
                active_instances += 1
                print(f"[ACTIVE CONNECTIONS] {active_instances}")
                if active_instances == 5:
                    for con  in connections:
                        con.send("start_game".encode(FORMAT))
            else:
                conn.send("Server Full".encode(FORMAT))
                print(f"Server is full. Denied entry to: {addr}")
        else: 
            conn.send("game_in_progress".encode(FORMAT))
            print(f"Game is in progress. Denied entry to: {addr}")

print("[STARTING] server is starting...")
start()

