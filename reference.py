
### basic function syntax

def add(x, y):
    return x + y


### Conditional (branching) statements

# if
# elif
# else

### Ways of handling errors

#### Ways of iterating
my_list = [1, 2, 3]
for x in my_list:
    pass

for x in range(len(my_list)):
    #loops over the indexes, not the values.
    print(my_list[x])

range(5) # return an iterator which you can't see
list(range(5))# turns a range into a list.

## Super fancy notation
with_one_more = [x + 1 for x in my_list]


# len()

# Ways of turning strings into numbers

len(my_string) # How many characters
ord(my_string[0]) # The letters.
###########
##### String methods
###########

my_string = "It is a truth universally acknowledged, that a man"

my_string.lower()
my_string.upper()

# Splitting.
my_string.split() # Splits on spaces
my_string.split("a") # Splits on the letter.
my_string.split("--") # Splits on the letter.

my_string[3:] # Third character from the end and so on--same as list.

# ord and chr.
ord(chr("A"))

#######################################################
## List methods
##
#######################################################
# list access methods

our_list = ["A", "B", "C", "D", "E"]

######################################################
##### Ways of getting single elements back. ##########
######################################################

# The first element (a letter)
our_list[0]
# The second element (a letter) (note the offsets.)
our_list[1]
# The last element
our_list[-1]
# The pre-ante-penultimate element
our_list[-4]

######################################################
########## Ways of getting lists back. ###############
######################################################

# The first two elements
our_list[0:2]
# OR
our_list[:2]

# The elements from 2 on
our_list[2:len(our_list)] # ugly!
our_list[2:] # Beautiful.

# The last two elements:
our_list[-2:]

### Fancy strides--ugly triple notation.
# Every other element from the first.
our_list[0::2]

# The list backward

our_list[-1::-1]
