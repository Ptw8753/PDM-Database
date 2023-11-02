from data_classes import User
import datetime
import random
import math

# Start and end date for ranges
START_DATETIME = datetime.datetime(2018, 1, 1, 0, 0, 0)     # January 1, 2018 at 12:00:00 AM
MIDDLE_DATETIME = datetime.datetime(2022, 12, 1, 0, 0, 0)   # December 1, 2022 at 12:00:00 AM
END_DATETIME = datetime.datetime(2022, 12, 31, 23, 59, 59)  # December 31, 2022 at 11:59:59 PM

# Generate 2^-i frequency distribution for i in [1:size]
# n(i) > 2 * n(i + 1) for all 1 <= i <= size
# n(i) != 0 for all 1 <= i <= size
# sum({n(i) for all 1 <= i <= size}) = 1
# limit size -> inf for get_inv2_frequencies(size) = [0.5, 0.25, 0.125, ...]
def get_inv2_frequencies(size):
    freqs = []
    norm = (2 ** size - 1) / 2 ** size
    for i in range(size):
        freq = 2 ** -(i + 1)
        freqs.append(freq / norm)
    return freqs

# Return an index given a list of frequencies for each index
# Sum of freqs should be 1
# freq(i) is the probability of i
def random_index_freq(freqs):
    total = 0
    rval = random.random()
    for i in range(len(freqs)):
        total += freqs[i]
        if rval < total:
            return i
    return len(freqs) - 1

# Return random disjoint subsets of a given list with size specified upon call
# List will be modified
def random_subset_without_replacement(ls, min_size, max_size, size_freqs = None):
    if size_freqs is not None: assert max_size - min_size == len(size_freqs) + 1
    random.shuffle(ls)
    i = 0
    while i < len(ls):
        size = random.randint(min_size, max_size) if size_freqs is None else random_index_freq(size_freqs) + min_size
        yield ls[i : i + size]
        i += size

# Return random subsets of a given list
def random_subset_with_replacement(ls, min_size, max_size, size_freqs = None):
    if size_freqs is not None: assert max_size - min_size == len(size_freqs) + 1
    while True:
        size = random.randint(min_size, max_size) if size_freqs is None else random_index_freq(size_freqs) + min_size
        yield random.choices(ls, k=size)

# Random datetime from uniform distribution
def random_datetime(start=START_DATETIME, end=END_DATETIME):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

# Random date from uniform distribution
def random_date(start=START_DATETIME, end=END_DATETIME):
    return random_datetime(start=START_DATETIME, end=END_DATETIME).date()

# Convert a python datetime to an sql datetime
def python_datetime_to_sql(python_dt : datetime.datetime):
    f = '%Y-%m-%d %H:%M:%S'
    return python_dt.strftime(f)

# Convert a python date to an sql date
def python_date_to_sql(python_d : datetime.date):
    f = '%Y-%m-%d'
    y, m, d = python_d.year, python_d.month, python_d.day
    python_dt = datetime.datetime(y, m, d, 0, 0)
    return python_dt.strftime(f)

# Convert an SQL date to a python date
def sql_date_to_python(sql_date):
    f = '%Y-%m-%d'
    print(sql_date)
    return datetime.datetime.strptime(sql_date, f)



def random_user_generator():
    """
    Generate random users
    
    Usage:
        user_generator = random_user_generator()
        for user in user_generator:                 # Will run forever
            print(user)
            
        or 
        
        user_generator = random_user_generator()
        for i in range(100):
            user = next(user_generator)
            print(user)
    """
    
    # Variables
    USERNAME_NUM_N_DIGITS = 5
    EMAIL_NUM_N_DIGITS = 3
    PASSWORD_N_DIGITS = 15
    EMAIL_SUFFIXES = ["@gmail.com", "@yahoo.com", "@outlook.com"]
    
    # Read in first and last names
    with open("first-names.txt") as f: first_names = [l.strip().replace("'", "") for l in f.readlines()]
    with open("last-names.txt") as f: last_names = [l.strip().replace("'", "") for l in f.readlines()]
    
    # Dictionary mapping initials to set of username number sequences already used
    username_num_map = dict()
    
    # Dictionary mapping first-name, last-name to set of email number sequences already used
    email_num_map = dict()
    
    while True:
        
        # Get first_name, last_name, username_prefix (initials), email_prefix (first+last name)
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Generate unique username
        username_prefix = first_name[0] + last_name[0]
        username_num = random.randint(1, (10 ** USERNAME_NUM_N_DIGITS) - 1)
        if username_prefix not in username_num_map: username_num_map[username_prefix] = set()
        while username_num in username_num_map[username_prefix]:
            username_num = ((username_num + 1) % ((10 ** USERNAME_NUM_N_DIGITS) - 1)) + 1
        username_suffix = ('0' * (USERNAME_NUM_N_DIGITS - math.ceil(math.log(username_num, 10)))) + str(username_num)   # Pad with zeros on the left
        username = username_prefix + username_suffix
        
        # Generate unique email
        email_prefix = first_name + last_name
        email_num = random.randint(1, (10 ** EMAIL_NUM_N_DIGITS) - 1)
        if email_prefix not in email_num_map: email_num_map[email_prefix] = set()
        while email_num in email_num_map[email_prefix]:
            email_num = ((email_num + 1) % ((10 ** EMAIL_NUM_N_DIGITS) - 1)) + 1
        email_midfix = ('0' * (EMAIL_NUM_N_DIGITS - math.ceil(math.log(email_num, 10)))) + str(email_num)               # Pad with zeros on the left
        email_suffix = random.choice(EMAIL_SUFFIXES)
        email = email_prefix + email_midfix + email_suffix
        
        # Generate password
        password_chars = []
        for i in range(PASSWORD_N_DIGITS):
            selector = random.randint(0, 2)
            if selector == 0:       # Digit
                c = chr(random.randint(ord('0'), ord('9')))
            elif selector == 1:     # Lowercase letter
                c = chr(random.randint(ord('a'), ord('z')))
            elif selector == 2:     # Uppercase letter
                c = chr(random.randint(ord('A'), ord('Z')))
            password_chars.append(c)
        password = "".join(password_chars)
        
        # Generate user creation date
        creation_date = random_datetime(start=START_DATETIME, end=MIDDLE_DATETIME).date()
        
        # Generate user last access date
        last_access_date = random_datetime(start=MIDDLE_DATETIME, end=END_DATETIME)
        
        # Create user
        yield User(username, password, first_name, last_name, email, creation_date, last_access_date)
    
    
if __name__ == "__main__":
    
    n_users = 1000000
    user_generator = random_user_generator()
    
    for i in range(n_users):
        user = next(user_generator)
        print(user)