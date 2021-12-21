## RECOMMENDED SCREEN WIDTH: 1920px, HEIGHT: 1080px ##

import socket
import time
import sys
import os
import pygame
from os import listdir
import tkinter as tk

root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_response = ''
current_coins = 0
username = ""
gameScreen = False
serverList = []
host = False
host_user = ""
busted_players = []
dealer_busted = False
payout = False
lost = False

while True:
    try:
        client.connect(ADDR)
        print("Connected to server!")
        break
    except ConnectionRefusedError or TimeoutError:
        print("Waiting for server to start...")
        time.sleep(5)


def get_response():
    while True:
        try:
            return client.recv(2048).decode(FORMAT)
        except ConnectionResetError:
            print("\nThe server has closed. ")
            os._exit(0)


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    try:
        client.send(send_length)
        client.send(message)

    except ConnectionResetError:
        print("You have been disconnected. \nThis window will close in 5 seconds.")
        time.sleep(5)
        sys.exit()


pygame.init()

white = (255, 255, 255)
grey = (10, 10, 10)
green = (0, 255, 0)
blue = (0, 0, 128)
black = (0, 0, 0)
red = (255, 0, 0)
dis_grey = (99, 99, 99)


X = screen_width  #1920
Y = screen_height-76  #1080
# X = 1920  #1920
# Y = 1011  #1080

display_surface = pygame.display.set_mode((X, Y), pygame.RESIZABLE)
pygame.display.set_caption('Black Jack')


def text_on_screen(string, font_size, colour, x_value, y_value, pos):
    font = pygame.font.Font('freesansbold.ttf', font_size)
    text = pygame.font.Font.render(font, string, True, colour)
    width, height = font.size(string)
    
    if pos == "center":
        display_surface.blit(text, (x_value - (width/2), y_value))
    elif pos == "left":
        display_surface.blit(text, (x_value - width, y_value))
    else:
        display_surface.blit(text, (x_value, y_value))


def u_input(x_value, y_value, input_width, input_height):
    font2 = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    input_box = pygame.Rect(x_value, y_value, input_width, input_height)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):
                    # Toggle the active variable.
                    active = not active
                else:
                    active = False
                # Change the current color of the input box.
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        # Render the current text.
        txt_surface = font2.render(text, True, color)
        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        # Blit the text.
        display_surface.blit(txt_surface, (input_box.x+5, input_box.y+5))
        # Blit the input_box rect.
        pygame.draw.rect(display_surface, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)


def game_loop(coins, game_screen, server_list, host):
    # start_game = False
    global username, busted_players, dealer_busted, payout, lost
    card_numbers = []
    once2 = True
    bet_inputted = False
    everyone_betted = False
    deck = sorted(listdir('cards'))
    bet_amount = ""

    image = pygame.image.load('cards/back.png')

    
    image = pygame.transform.scale(image, (207, 300))
    small_back = pygame.transform.scale(image, (125, 182))

    text_on_screen("Black Jack", 120, white, (X/2), 100, "center")
    text_on_screen("Enter User Name: ", 30, white, (X/2) - 150, 250, "center")
    username = u_input((X/2), 250, 140, 32)
    send(username)
    game_screen = False
    player_turn = ""
    game_started = False
    status = ""
    dealer_card = ""
    dealer_card_nums = []
    turn = False
    while True:
        try:
            server_response = get_response()
            # print(server_response)
            if server_response == "Server Full":
                text_on_screen("Server is full. Please try again later.", 60, white, (X/2), 100, "center")
            elif "game_in_progress" == server_response:
                text_on_screen("A game is currently in progress. Added to cue...", 30, white, (X/2), 100, "center")

            elif server_response == "!@#$%^&*() Main Menu !@#$%^&*()":
                text_on_screen("Black Jack", 120, white, (X/2), 100, "center")
                text_on_screen("Enter User Name: ", 30, white, (X/2) - 150, 250, "center")
                username = u_input((X/2), 250, 140, 32)
                send(username)
                game_screen = False

            elif server_response == "!@#$%^&*() Game Screen !@#$%^&*()":
                display_surface.fill(grey)
                game_screen = True

            elif "coin" in server_response:  
                coins = int(server_response.replace("coins: ", ""))

            elif "dealer_card_numbers: " in server_response:
                dealer_card_nums.clear()
                dealer_card_nums = (server_response.replace("dealer_card_numbers: ", "")).split(" ")
                
            
            elif "dealer_card: " in server_response:
                dealer_card_nums.clear()
                dealer_card = int(server_response.replace("dealer_card: ", ""))
                dealer_card_nums.append(dealer_card)

            elif "card_numbers" in server_response:
                everyone_betted = True
                card_num = server_response.replace("card_numbers: ", "")
                card_numbers = card_num.split(" ")
            
            elif "user_num_of_cards: " in server_response:
                user_turn_num_cards = server_response.replace("user_num_of_cards: ", "")
            
            elif "player_turn: " in server_response:
                player_turn = server_response.replace("player_turn: ", "")
            
            elif "bust: " in server_response:
                server_response = server_response.replace("bust: ", "")
                busted_players.append(server_response)
                if server_response == "dealer":
                    dealer_busted = True
                    if username in busted_players:
                        lost = True
                    else:
                        payout = True
            elif "payout" in server_response:
                payout = True
                print("payout")
            
            elif "lost" in server_response:
                print("lost")
                lost = True
                status = "You have lost your bet! "

            elif "people in room: " in server_response:
                room = server_response.split("\n")
                
                room.remove("people in room: ")
                server_list = room


            elif "start_game" in server_response:
                game_started = True
            if game_screen:
                # Background 
                display_surface.fill(grey)

                # Coins
                text_on_screen("Coins: " + str(coins), 30, white, 115, 100, "center")

                # player turn (status)
                if not lost or not payout:
                    if player_turn != "":
                        if player_turn != username:
                            out_player = player_turn.split(" (bet amount: ")
                            status = out_player[0] + "'s turn."
                        else: 
                            status = "Your turn."
                            turn = True

                # player's cards 
                if host:
                    text_on_screen("You (host): ", 20, white, 350, 610, "right")
                    if not game_started:
                        start_game_rect = pygame.draw.rect(display_surface, green, (40, 550, 210, 70))
                        text_on_screen("Start Game >>", 28, white, 145, 572, "center")
                else:
                    text_on_screen("You: ", 20, white, 350, 610, "right")
                if len(card_numbers) > 0:
                    for x in range(len(card_numbers)):
                        u_card = pygame.image.load(f'cards/{(deck[(int(card_numbers[x])-1)])}')
                        u_card = pygame.transform.scale(u_card, (207, 300))
                        display_surface.blit(u_card, ((350 + x*75), 650))
                
                else:
                    for x in range(2):
                        display_surface.blit(image, ((350 + x*75), 650))
                if username in busted_players:
                    text_on_screen("BUSTED!", 60, red, 420, 680, "right")
                    if once2:
                        send("pass")
                        once2 = False

                # dealer's cards
                text_on_screen("Dealer: ", 20, white, 350, 200, "right")
                if dealer_busted:
                    text_on_screen("BUSTED!", 40, white, 420, 200, "right")
                if payout:
                    status = "You won! Paying " + str(int(round(float(bet_amount)*1.5))) + " coins."
                    if coins <= (coins + int(round(float(bet_amount)*1.5))):
                        coins += 1
                        text_on_screen(f"+ {coins + int(round(float(bet_amount)*1.5))} coins", 12, green, 115, 150, "center")
                if len(dealer_card_nums) < 2:
                    for x in range(2):
                        if dealer_card and x == 0:
                            dealer_card_img = pygame.image.load(f'cards/{(deck[(int(dealer_card)-1)])}') 
                            dealer_card_img = pygame.transform.scale(dealer_card_img, (207, 300))
                            display_surface.blit(dealer_card_img, ((350 + x*75), 240))
                        else:
                            display_surface.blit(image, ((350 + x*75), 240))
                else:
                    for count, x in enumerate(dealer_card_nums):
                        dealer_card_img = pygame.image.load(f'cards/{(deck[(int(x)-1)])}') 
                        dealer_card_img = pygame.transform.scale(dealer_card_img, (207, 300))
                        display_surface.blit(dealer_card_img, ((350 + count*75), 240))


                # Divider line (left)
                pygame.draw.line(display_surface, white, (300, 0), (300, 1011), width=1)

                # divider line (right)
                pygame.draw.line(display_surface, white, (1340, 0), (1340, 1011), width=1)

                # people on server
                text_on_screen("People in room: ", 30, white, 1630, 5, "center")

                if not everyone_betted:
                    hit_rect = pygame.draw.rect(display_surface, dis_grey, (40, 200, 210, 80))
                    pass_rect = pygame.draw.rect(display_surface, dis_grey, (40, 320, 210, 80))
                else:
                    pygame.draw.rect(display_surface, red, (40, 200, 210, 80))
                    pygame.draw.rect(display_surface, blue, (40, 320, 210, 80))
                
                text_on_screen("HIT", 65, white, 145, 208, "center")
                text_on_screen("PASS", 65, white, 145, 332, "center")

                # Users List
                y_pos = 70
                counter = 1
                for x in range(len(server_list)):
                    if username != server_list[x]:
                        text_on_screen((str(counter) + ". " + str(server_list[x])), 12, white, 1400, y_pos, "right")
                        if server_list[x] in busted_players:
                            text_on_screen("BUSTED", 45, white, 1450, y_pos+25, "right")
                        else:
                            for x in range(2): 
                                display_surface.blit(small_back, ((1450 + x*50), y_pos+12))
                        y_pos += 250
                        counter += 1
                if len(server_list) == 1:
                    text_on_screen("No one else is in the room. ", 10, white, 1630, 100, "center")
                if server_list and not host and server_list[0] == username:
                    host = True

                if game_started:
                    
                    if not bet_inputted:
                        if host:
                            status = "You started the game! Place your bets."
                        else:
                            status = str(server_list[0]) + " started the game! Place your bets."

                        text_on_screen(status, 35, white, 820, 100, "center") 
                        text_on_screen("BET", 65, white, 145, 550, "center")
                        bet_amount = u_input(50, 635, 72, 35)
                        coins -= int(bet_amount)
                        send("bet_amount " + username + " " + str(bet_amount))
                        username += (f" (bet amount: {bet_amount})")
                        bet_inputted = True

            
            # Status 
            text_on_screen(status, 35, white, 800, 100, "center") 
                

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not game_started and host:
                        if start_game_rect.collidepoint(event.pos):
                            text_on_screen("processing.....", 10, white, 145, 620, "center") 
                            pygame.display.update()
                            send("start_game")
                            game_started = True
                    if hit_rect.collidepoint(event.pos):
                        if not everyone_betted:
                            text_on_screen("Please wait for the game to start!!", 15, red, 35, 282, "right")
                            pygame.display.update()
                        if turn:
                            send("hit")
                    if pass_rect.collidepoint(event.pos):
                        if not everyone_betted:
                            text_on_screen("Please wait for the game to start!!", 15, red, 35, 282, "right")
                            pygame.display.update()
                        if turn:
                            send("pass")




                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
        except ValueError:
            print("value error.")


game_loop(current_coins, gameScreen, serverList, host)

