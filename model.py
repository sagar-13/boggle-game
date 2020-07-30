
from tkinter import *
from tkinter.ttk import *
from enchant import *
from itertools import *
import random

'''
The model which handles the underlying game behaviour
'''
    
class GridModel:
    ''' current_grid is the grid generated by the View or passed from a loaded game
        loaded_records (optional) if game is being loaded 
    '''

    def __init__(self, current_grid, loaded_records = []):
        
        self.current_grid = current_grid
        self.grid_letters = []
        self.letters = {}
        self.scored_words = []
        self.english_dictionary = Dict("en_US")

        for word in loaded_records:
            if len(word) > 2:
                self.scored_words.append(word.rstrip())


        ''' Create a GridLetter object for each dice on the grid, store the letters in 
        grid_letters as a list but also in self.letters dictionary where the value is a list
        This will allow keeping track of multiple occurences of the same letter'''
        index = 0
        for element in self.current_grid:
            entry = GridLetter(self.current_grid, index)
            self.grid_letters.append(entry)
            if element in self.letters:
                self.letters[element].append(entry)
            else:
                self.letters[element] = [entry]
            index +=1
 
    ''' Solution checking '''
    def check_word(self, word):
        
        word = word.upper()
  
        if word in self.scored_words:
            print('Word already done')
            return False
        
        if len(word) <3:
            print('Word too short')
            return False
        
        if not self.english_dictionary.check(word):
            print('That is not english.')
            return False
        
        # Get all permutations of the word and remove repeats
        perms = []
        for perm in [''.join(l) for l in permutations(word, len(word))]:
            if perm[0] <= perm[-1]:
                perms.append(perm)
        # for each permutation, use a recursive helper function to check the grid
        for combo in perms:
            print("\nNEW COMBO BEGINS: ", combo)
            first_char = combo[0]
            if first_char == "Q": first_char = "QU"

            # if the letter even exists on the grid, then continue
            if first_char in self.letters:
                if self.is_possible(combo, self.letters[first_char], set()):
                    self.scored_words.append(word.strip())
                    
                    return True
            
        print("end")
        return False
        
    ''' recursive helper function for checking if a word is on the grid 
    takes the word, possible GridLetter objects where it could start, and a set 
    of used indexes'''
    def is_possible(self, word, possible_starts, used = set()):
        
        # base case
        if len(word) == 1:
            print("base: ", word)
            return True
        # Handle Q = QU              
        first_char = word[0]
        if first_char == "Q": first_char = "QU"

        #if the character is not in the grid
        if not first_char in list(self.letters.keys()):
            print("not in letters: ", word)
            return False

        # Evaluate each possible option (recursive call)
        print(word, ",possible starts: ", possible_starts)
        for start in possible_starts:
            used.add(start.get_index())
            new_starts = []
            #For each possible starting option, check adjacent indexes
            adj = start.get_adjacent()
            for entry in adj.values():
                
                if first_char == "QU": next = 2
                else: next = 1
                
                # if the adjacent index is correct and has not been used before
                if(entry[0]) == word[next] and (entry[1] not in used):
                    print(entry, " is ", word[next])
                    a = [x for x in used]
                    print(entry[1], " is not in", a)
                   
                    used.add(entry[1])
                    new_starts.append(self.grid_letters[entry[1]])
                    
                    # recurse on the substring
                    result = self.is_possible(word[next:], new_starts, used)
                    
                    if result: return True
            
    ''' allocates points basedo n the boggle points system'''
    def calculate_points(self):
        points = 0
        point_dict = {3:1, 4:1, 5:2, 6:3, 7:5, 8:11}
        for word in self.scored_words:
            
            word_length = len(word)
            if word_length in point_dict.keys():
                points += point_dict[word_length]
            elif word_length>8:
                points += 11
    
        return points
    


''' An object represented by one dice in the game of boggle. Given the entire grid
as a list and it's own index, this class provides information about the nature of a 
grid letter relative to other letters and helps perform some of the necessary logic 
calculations'''
class GridLetter:
    def __init__(self, current_grid, index):
        self.index = index 
        self.current_grid = current_grid
        self.self = self.current_grid[index]
    
        # GET ALL ADJACENT INDEXES
        if self.index < 12:
            self.bottom = self.index + 4
        else: self.bottom = None

        if self.index>3:
            self.top = self.index - 4
        else: self.top = None

        if self.index in [3,7,11,15]:
            self.right = None
        else: 
            self.right = self.index + 1

        if self.index in [0,4,8,12]:
            self.left = None
        else: 
            self.left = self.index - 1
        
        if self.top != None and self.right != None:
            self.topright = self.top + 1
        else: self.topright = None
        
        if self.bottom != None and self.right != None:
            self.bottomright = self.bottom + 1
        else: self.bottomright = None

        if self.top != None and self.left != None:
            self.topleft = self.top - 1
        else: self.topleft = None

        if self.bottom != None and self.left != None:
            self.bottomleft = self.bottom - 1
        else: self.bottomleft = None

        # Populate a dictionary with the adjacent index for easy reference
        self.adjacent_indexes = {"top": self.top, "right": self.right, 
        "bottom":self.bottom, "left": self.left, "topright": self.topright, 
        "bottomright": self.bottomright, "bottomleft": self.bottomleft, "topleft":self.topleft}
        
        # Create a dictionary like adjacent_indexes except the values are tuples (letter, index)
        self.adjacent_letters = {}
        for (key, value) in self.adjacent_indexes.items():
            if value != None:
                self.adjacent_letters[key] = (self.current_grid[value], value)
        
    def __repr__(self):
        return self.self + " GridLetter at index: " + str(self.index)
    
    # Getters
    def get_adjacent(self):
        return self.adjacent_letters

    def get_index(self):
        return self.index

    def __eq__(self, value):
        return self.index == value.index