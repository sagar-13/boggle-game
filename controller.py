from model import *
from view import *
import tkinter as tk
from tkinter.ttk import *
import datetime
import random
from tkinter import filedialog


'''Creates the model, view, and controller for the application and runs it.
'''
class Controller:
    
    def __init__(self):

        self.root = tk.Tk()
        self.view = View(self.root, self)
        # pass the initial grid generated in the view to the model
        self.model = GridModel(self.view.get_grid())

        self.root.mainloop()

    '''Verifies the validity of a word in the model, used to update the view'''
    
    def check_word(self, word):
        return self.model.check_word(word)
    
    '''Gets score from the model, used to update the view'''
    def get_score(self):
        return self.model.calculate_points()
    
    '''Logic for new game'''
    def new_game(self, grid=[], records=[]):
        #optional parameters for loading a game: grid, records
        self.root.destroy()
        # Create a new instance of the game
        self.root = tk.Tk()
        self.view = View(self.root, self, grid, records)
        self.model = GridModel(self.view.get_grid(), records)
        self.view.update_score()
        self.root.mainloop()
    
    '''Save a file to the same directory as controller.py'''
    def save_game(self, records, current_grid):
        try: 
            # Format save file name with current date
            now = datetime.datetime.now()
            time_string = now.strftime("%b-%d-%Y, %H%M%S")
            save_name = "save_file_" + time_string + ".txt"
            with open(save_name, 'w') as savefile:
                # first line is grid, subsequent lines are current scored words
                savefile.write(''.join(current_grid))
                savefile.write("\n")
                savefile.write(records)
        except FileNotFoundError:
            print("\nThe program could not save the file \n")  
    
        return save_name # Return is to give user feedback in the view

    ''' open a game saved with with save_game'''
    def load_game(self, filename):
        
            with open(filename, 'r') as savefile:
    
                lines = savefile.readlines()
                words = lines[1:]
                grid = lines[0].strip()
                self.new_game(grid, lines[1:])
  

                 
if __name__ == "__main__":
    app = Controller()
