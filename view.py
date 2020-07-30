
from tkinter import *
from tkinter.ttk import *
import tkinter as tk
import tkinter.font as font
import re
from tkinter import messagebox
from tkinter import filedialog
import random
from model import *
from view import *


''' The visual interface for the application'''
class View():

    def __init__(self, root, controller, grid=[], records = []):
        
        # The controller passes an instance of itself as well as the top level root
        # grid and records are for the case where the game is being loaded 

        self.controller = controller
        self.root = root
        Grid.rowconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 0, weight=1)
        self.root.title("Play Boggle!")
    
        self.current_grid = []
        self.diceRows = [['A', 'E', 'A', 'N', 'E', 'G'] ,
                    [ 'A', 'H', 'S', 'P', 'C', 'O'] ,
                    [ 'A', 'S', 'P', 'F', 'F', 'K'] ,
                    [ 'O', 'B', 'J', 'O', 'A', 'B'] ,
                    [ 'I', 'O', 'T', 'M', 'U', 'C'] ,
                    [ 'R', 'Y', 'V', 'D', 'E', 'L'] ,
                    [ 'L', 'R', 'E', 'I', 'X', 'D'] ,
                    [ 'E', 'I', 'U', 'N', 'E', 'S'] ,
                    [ 'W', 'N', 'G', 'E', 'E', 'H'] ,
                    [ 'L', 'N', 'H', 'N', 'R', 'Z'] ,
                    [ 'T', 'S', 'T', 'I', 'Y', 'D'] ,
                    [ 'O', 'W', 'T', 'O', 'A', 'T'] ,
                    [ 'E', 'R', 'T', 'T', 'Y', 'L'] ,
                    [ 'T', 'O', 'E', 'S', 'S', 'I'] ,
                    [ 'T', 'E', 'R', 'W', 'H', 'V'] ,
                    [ 'N', 'U', 'I', 'H', 'M', 'QU']
                    ]
  
         # Styling and Tkinter macOS bug adjustments
        self.font = "Roboto"
        self.background="#F1FBF7"
        self.root.option_add('*tearOff', FALSE)
        self.root.configure(background=self.background)
        style = Style()
        style.theme_use('classic') 
        style.configure("TButton",
            highlightcolor="#216657", background="#39A78E", 
            foreground="white", relief="flat", font=(self.font, 20))

        # Frame for the letter grid
        self.dice_grid_frame = tk.Frame(self.root)

        # if the game is new, populate current grid with a new random grid, 
        # otherwise load the existing grid
        if grid == []:
            self.grid_maker()
        else:
            self.load_grid(grid)

        self.dice_grid_frame.configure(background=self.background)
        self.dice_grid_frame.grid(row=0, column=0, columnspan=4, rowspan=4, sticky=N+S+E+W)

        # Other elements of game GUI, place directly on the top level root
        self.editing_label = Label(self.root, text="Input word and press Enter:\n", 
            font=(self.font, 20), background=self.background, width=30, )
        self.editing_line = Entry(self.root, font=(self.font, 20), background=self.background)
        self.editing_line.bind('<Return>', self.submit_word)
        
        self.error_label = Label(self.root, text="...",font=(self.font, 20), width=10, background=self.background)
       
        self.scoreVar = StringVar()
        self.scoreVar.set("Score: 0")
        self.score = Label(self.root, textvariable=self.scoreVar, font=(self.font, 25), 
        background=self.background, width=10, relief=SOLID, padding=20)
        
        self.records = Text(root, width=15, font=(self.font, 20), background=self.background, foreground="green", highlightbackground="black")
        self.records.config(state="disabled")
        
        self.score_btn = Button(self.root, text="End Game", style="TButton", command=self.end_game)
        
        # if the game is being loaded, add the words from the old save game
        # also update the score
        if records != []:
            for word in records:
                if len(word) > 2:
                    self.records.config(state="normal")
                    self.records.insert(END, word)
                    self.records.config(state="disabled")
            self.update_score()
            self.scoreVar.set("Score: " + str(self.controller.get_score()))
            
        # GRID
        self.editing_label.grid(row=5, padx=10, pady=3, columnspan=4)
        self.editing_line.grid(row=6, padx=10, pady=10)
        self.error_label.grid(row=6, column=1, padx=10, pady=10)
        self.score.grid(row=0, column=6,columnspan=10,padx=5, pady=5)
        self.records.grid(row=1, column=6, columnspan=2,padx=5, pady=5)
        self.score_btn.grid(row=2, column=6, padx=5, pady=5)

        # MENU CREATION
        # magic names for each menu
        if (self.root.tk.call('tk', 'windowingsystem') != "win32"):
            menubar = Menu(self.root, name="apple")
        else: 
            menubar = Menu(self.root, name="system")
       
        # File Menu
        menu_file = Menu(menubar)
        menu_file.add_command(label="New Game", command=self.new_game)
        menu_file.add_command(label="Save Game", command=self.save_game)
        menu_file.add_command(label="Load Game", command=self.load_game)
        menu_file.add_command(label="End Game", command=self.end_game)
        menu_file.add_command(label="Quit", command=self.quit_game)
        menubar.add_cascade(menu=menu_file, label="Game")
        help_menu = Menu(menubar, name="help")
        window_menu = Menu(menubar, name="window")
        menubar.add_cascade(menu=help_menu, label="Help")
        menubar.add_cascade(menu=window_menu, label="Window")
        self.root['menu'] = menubar

    
    def get_grid(self):
        '''
        The grid is created in the View using grid_maker,
        including the randomization of the dice. 
        The controller needs to know what dice values were selected
        to pass to the model.
        '''
        return self.current_grid

    def submit_word(self,event):
        '''
        Checks if the current word in the editing line is valid
        '''
        # Controller checks
        valid = self.controller.check_word(self.editing_line.get())
        
        # User Feedback for each case
        if valid:
            validtext = self.editing_line.get() + " is valid!"
            self.error_label.configure(text=validtext, foreground="green")
            # Update records view, and disable after (READ ONLY)
            self.records.config(state="normal")
            self.records.insert(END, self.editing_line.get().upper() + "\n")
            self.editing_line.delete(0, 'end')
            self.records.config(state="disabled")
            self.update_score()
        else:
            self.error_label.configure(text="Invalid Word!", foreground="red")

    def update_score(self):
        '''Update the score in the view'''
        self.scoreVar.set("Score: " + str(self.controller.get_score()))

    ''' Next 4 functions handle the logic for new games, saving, loading, and quitting'''
    def new_game(self):
        if messagebox.askyesno(title="New Game?", 
        message="Are you sure you would like to abandon the current game?"):
            self.controller.new_game()
            self.scoreVar.set("Score: ")
     
    def save_game(self):
        if messagebox.askyesno(title="Save Game?", 
        message="Would you like to save the current game?"):
            # Pass current records and grid to the controller so it can save the game.
            records = self.records.get("1.0",END)           
            savename = self.controller.save_game(records, self.current_grid)
            messagebox.showinfo("Saved!", ("Game saved as " + savename))

    def load_game(self):
        if messagebox.askyesno(title="Load Game?", message="Would you like to load an existing save file?"):
            # Ask the user for a file a load it. 
            filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("txt files","*.txt"),("all files","*.*")))
            self.controller.load_game(filename)
            self.update_score()

    def end_game(self):
        if messagebox.askyesno(title="End Game?", message="Would you like to end the game?"):
            # If the user wishes to end the game, lock the current game and provide a message.
            self.editing_line.config(state=DISABLED)
            final_message = ("The game has ended. Final " + self.scoreVar.get() +
                ". \nPlay again using the game menu!")
            self.editing_label.config(text=final_message)
                
    def quit_game(self):
        if messagebox.askyesno(title="Quit?", message="Would you like to quit the game?"):
            self.root.destroy()
            quit()
    
    ''' 
    iterate through self.diceRows, create each row for the game
    with randomized values
    '''
    def grid_maker(self):
        
        lower = 0
        upper = 4
        row_count = 0
        while upper <= 16:
            col_count = 0
            # Creating one row at a time (4 values) Using lower/upper for list slicing
            for row in self.diceRows[lower:upper]:
                Grid.rowconfigure(self.dice_grid_frame, row_count, weight=1)
                Grid.columnconfigure(self.dice_grid_frame, col_count, weight=1)
                rand_index = random.randint(0, 5)
                self.current_grid.append(row[rand_index])
                letterLabel = tk.Label(self.dice_grid_frame, text=row[rand_index], background=self.background,
                    foreground="black", relief="solid", font=(self.font, 30), padx=10, pady=10)
                letterLabel.grid(row=row_count, column=col_count)
                
                col_count +=1
            row_count +=1
            upper += 4
            lower += 4

    '''Same as above but uses an already provided grid''' 
    def load_grid(self, grid):
        
        lower = 0
        upper = 4
        row_count = 0
        while upper <= 16:
            col_count = 0
            for item in grid[lower:upper]:
                Grid.rowconfigure(self.dice_grid_frame, row_count, weight=1)
                Grid.columnconfigure(self.dice_grid_frame, col_count, weight=1)
                self.current_grid.append(item)
                letterLabel = tk.Label(self.dice_grid_frame, text=item, background=self.background,
                    foreground="dark green", relief="solid", font=(self.font, 30), padx=10, pady=10)
                letterLabel.grid(row=row_count, column=col_count,padx=10, pady=10)
                
                col_count +=1

            row_count +=1
            upper += 4
            lower += 4

        
        

    
   