import pygame as pyg 
import json  # for high score. was originally going to tackle it with txt file handling but a friend of mine recommended/taught me to use this method so giving it a shot
import os  # some file operations here and there, was used only once or twice
import random  # for making the randomized grid numbers

'''
S to show solution
Esc to play if in solution state
Esc to pause if in play state
'''





# Constants
GS = 5  # grid size, can be changed to any number up until 14 (after that the window becomes too big for my monitor at least)
CS = 60  # size of each cell in pixels
MG = 20  # margin size
AR = 16/10
SW = GS * CS + 2 * MG + 150  # width = size of each cell * number of cells + margin sizes + 150 for extra space at the right side to show score
SH = GS * CS + 2 * MG  # height
BL = (0, 0, 255)  # blue
WH = (255, 255, 255)  # white
BK = (0, 0, 0)  # black
GY = (200, 200, 200)  # gray
RD = (255, 0, 0)  # red

class GameState: #used to determine state in which the game is in rn
    MENU = 0  # Menu
    PLAY = 1  # Playing 
    PAUS = 2  # Paused 
    OVER = 3  # Game over 
    SOLN = 4  # Show solution 

# loading high scores from ht ehighsore.json file
def load_hs():
    try:
        with open("hs.json", "r") as f:  # basic file handling
            data = json.load(f)  
            return data.get("hs", 0) 
    except FileNotFoundError:
        return 0 

# saving high score
def save_hs(score):
    with open("hs.json", "w") as f:  
        json.dump({"hs": score}, f) 

# puzzle generation
def gen_puz():
    grid = [[0] * GS for _ in range(GS)]  # make an empty array/grid
    sol = [[random.randint(0, 1) for _ in range(GS)] for _ in range(GS)]  # make a solution 

    # was originally going to have a hint button and all but decided to not follow through. take hints to mean the numbers at the sides like 5 or "3 1" and so on
    def gen_hint(arr):
        hints = [] 
        cnt = 0 
        for val in arr:
            if val == 1: 
                cnt += 1 
            elif cnt > 0:
                hints.append(str(cnt)) 
                cnt = 0  
        if cnt > 0: 
            hints.append(str(cnt))  
        return " ".join(hints) if hints else "0" 

    rh = [gen_hint(row) for row in sol] 
    ch = [gen_hint(col) for col in zip(*sol)]

    return rh, ch, sol, grid 

# checks if the current grid is correct or not
def check_sol(grid, sol):
    for r in range(GS):
        for c in range(GS):
            if grid[r][c] != sol[r][c]:
                return False  
    return True  

# draws all sorts of stuff like grid cells errors etc
def draw_grid(sc, grid, rh, ch, wg=None):
    for r in range(GS):
        for c in range(GS):
            clr = WH  # colour of cell by default
            if grid[r][c] == 1: 
                clr = BL  # changes cell to blue if cell is correct
            if wg and wg[r][c] == 1:  
                clr = RD  # set color to red if cell is incorrect
            pyg.draw.rect( 
                sc,
                clr,
                (MG + c * CS, MG + r * CS, CS, CS),
            )
            pyg.draw.rect( 
                sc,
                BK,
                (MG + c * CS, MG + r * CS, CS, CS),
                1,
            )

    # rows
    fnt = pyg.font.Font(None, 24) 
    for i, h in enumerate(rh):  
        txt = fnt.render(h, True, BK)  
        sc.blit(txt, (MG / 2, MG + i * CS + CS / 3)) 

    # column
    for i, h in enumerate(ch): 
        txt = fnt.render(h, True, BK) 
        sc.blit(txt, (MG + i * CS + CS / 3, MG / 2)) 

# menu screen
def draw_menu(sc, title, opts):
    sc.fill(GY)  
    fnt_t = pyg.font.Font(None, 48)  
    fnt_o = pyg.font.Font(None, 36) 
    txt_t = fnt_t.render(title, True, BK)  
    sc.blit( 
        txt_t,
        (SW / 2 - txt_t.get_width() / 2, SH / 4),
    )
    for i, opt in enumerate(opts):  
        txt_o = fnt_o.render(opt, True, BK)  # text
        sc.blit(  # 3
            txt_o,
            (
                SW / 2 - txt_o.get_width() / 2,
                SH / 2 + i * 50,
            ),
        )

# draw the score
def draw_sc(sc, score):
    fnt = pyg.font.Font(None, 24) 
    txt = fnt.render(f"Score: {score}", True, BK) 
    sc.blit(txt, (SW - 100, 10)) 

def main(): # mostly calling the functions with a few checks for things such as wrong clicks and all
    pyg.init()
    sc = pyg.display.set_mode((SW, SH))  
    pyg.display.set_caption("Block Logic")  

    state = GameState.MENU  # set initial state to main menu
    hs = load_hs() 
    rh, ch, sol, grid = gen_puz()  
    score = 0  
    wc = 0  # used to see how many wrong clicks player has made, max of 3
    wg = [[0] * GS for _ in range(GS)]  # wrong click grid

    run = True  # flag for while loop
    while run:
        for ev in pyg.event.get():  # event hanler
            if ev.type == pyg.QUIT:  # close window
                run = False 
            if state == GameState.MENU:  # if in main menu
                if ev.type == pyg.MOUSEBUTTONDOWN:  # is screen is clicked
                    mp = pyg.mouse.get_pos()  # mouse position
                    fnt_o = pyg.font.Font(None, 36) 
                    txt_o = fnt_o.render("Play", True, BK) 
                    rect_o = txt_o.get_rect(center=(SW / 2, SH / 2))  
                    if rect_o.collidepoint(mp):  # for some reason the actual box where the code considers "play" is higher than the play text. tried setting the position manually but it didnt wor out if I changed grid size or aspect ratio.
                        state = GameState.PLAY  
                        rh, ch, sol, grid = gen_puz()  
                        score = 0 
                        wc = 0 
                        wg = [[0] * GS for _ in range(GS)]  
            elif state == GameState.PLAY:  # here onwards its checking for the gameplay stuff
                if ev.type == pyg.MOUSEBUTTONDOWN:  
                    mp = pyg.mouse.get_pos()  
                    if (  # if mouse position was in the grid boundary
                        MG <= mp[0] <= MG + GS * CS
                        and MG <= mp[1] <= MG + GS * CS
                    ):
                        c = (mp[0] - MG) // CS # find index of the grid
                        r = (mp[1] - MG) // CS  
                        grid[r][c] = 1 - grid[r][c]  # chnage the cells properties
                        if grid[r][c] != sol[r][c]:  # if incorrect
                            wc += 1  # strike 1
                            wg[r][c] = 1  # mark cell as clicked and incorrect
                            if wc >= 3:  # game over condition
                                fnt = pyg.font.Font(None, 36) 
                                txt = fnt.render("Retry!", True, RD) 
                                sc.blit(txt, (SW / 2 - txt.get_width() / 2, SH / 2 - txt.get_height() / 2)) 
                                pyg.display.flip()  # display update
                                pyg.time.delay(1000)  # wait for a second
                                score = 0  # reset score
                                wc = 0  # reset wrong clicks
                                rh, ch, sol, grid = gen_puz()  # new puzzle
                                wg = [[0] * GS for _ in range(GS)]  # reset wrong clicks grid
                        else:  # if correct
                            wg[r][c] = 0  # unmark the cell as incorrect, was getting an error where if you clicked the correct cell again it would permanently be red
                        if check_sol(grid, sol):  # if solved
                            score += 1  # increment score
                            if score > hs: 
                                hs = score  # update high score
                                save_hs(hs)  # save high score
                            rh, ch, sol, grid = gen_puz()  # new puzzle
                            fnt = pyg.font.Font(None, 36)  
                            txt = fnt.render("Good job!", True, BK)  # motivation
                            sc.blit(txt, (SW / 2 - txt.get_width() / 2, SH / 2 - txt.get_height() / 2))  
                            pyg.display.flip() 
                            pyg.time.delay(1000) 
                            wg = [[0] * GS for _ in range(GS)] 
                if ev.type == pyg.KEYDOWN:  # if key is pressed
                    if ev.key == pyg.K_s: 
                        state = GameState.SOLN 
                    if ev.key == pyg.K_ESCAPE:  
                        state = GameState.PAUS 
            elif state == GameState.PAUS:  
                if ev.type == pyg.KEYDOWN:  
                    if ev.key == pyg.K_ESCAPE: 
                        state = GameState.PLAY  
            elif state == GameState.OVER: 
                if ev.type == pyg.MOUSEBUTTONDOWN: 
                    state = GameState.MENU 
            elif state == GameState.SOLN: 
                if ev.type == pyg.KEYDOWN: 
                    if ev.key == pyg.K_ESCAPE: 
                        state = GameState.PLAY 

        sc.fill(WH)  # white screen bg

        if state == GameState.MENU:  # draw stuff based on current state like main menu or grid
            draw_menu(sc, "Block Logic", ["Play", f"High Score: {hs}"]) 
        elif state == GameState.PLAY: 
            draw_grid(sc, grid, rh, ch, wg) 
        elif state == GameState.PAUS: 
            draw_menu(sc, "Paused", ["Resume"])
            draw_grid(sc, grid, rh, ch, wg)  
        elif state == GameState.OVER:  
            draw_menu(sc, "Game Over", [f"Score: {score}", "Main Menu"])  
        elif state == GameState.SOLN:  
            draw_grid(sc, sol, rh, ch) 

        draw_sc(sc, score) 
        pyg.display.flip() 

    pyg.quit() 

if __name__ == "__main__":
    main()  # run