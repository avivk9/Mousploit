import sqlite3

def read_database_table(database, table):
    """
    This function receives the SQLite database filename and a table name. It returns all rows from that table as a list of tuples.
    """
    records = []
    try:
        sqlite_connection = sqlite3.connect(database)
        cursor = sqlite_connection.cursor()
 
        sqlite_select_query = "SELECT * FROM " + table
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to read data from sqlite table:" + table, error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
    return records
 

def choose_row(database, table, excluded_columns = []):
    """
    This function receives the SQLite database filename, a table name and an optional list containing indices of columns to exclude from display.
    It retrieves all rows of the table from the DB, prints them for the user to choose from and takes the input.
    """
    tmp_table = read_database_table(database, table)
    print(table + " fetched from DB:") # e.g. DEVICES fetched from DB:

    # calculating the max width of each column in the table, to use a correct fixed width when printing
    max_widths = []
    for j in range(len(tmp_table[0])):
        max_widths.append(max([len(str(tmp_table[i][j])) for i in range(len(tmp_table))]))
    
    # printing the table
    for i in range(len(tmp_table)):
        print(f"{i + 1}".rjust(max_widths[0]) + ".   ", end="") # printing the serial number of the row (with a fixed width according to the max width of the id field)
        for j in range(1, len(tmp_table[i])): # iterating over the columns excluding the first one (id)
            if j not in excluded_columns: # not printing a column if it's excluded
                print(tmp_table[i][j].ljust(max_widths[j]) + "   ", end="") # printing the current value with a fixed width according to the max width of the column
        print() # print a new line at the end of each row

    # receive selection from the user
    num = int(input("Select row (0 for manual): "))
    if num == 0: # if the user wants to enter the parameters (address, vendor, etc.) manually
        return None
    else:
        return tmp_table[num - 1] # return the chosen row
    