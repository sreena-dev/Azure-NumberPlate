import pyodbc

# Connection details
server = 'serverocr.database.windows.net'
database = 'License-Plate-DB'
username = 'ggrserver'
password = 'License-Plate-DB'

# Function to create a connection
def create_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )

# Function to execute any query (insert, delete, select)
def execute_query(query, params=None, fetch=False):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        
        # Commit changes if it's not a select query
        if not fetch:
            conn.commit()
            print("Operation successful!")
        else:
            # Fetch results if it's a select query
            result = cursor.fetchall()
            return result
        
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        conn.close()

# Function to insert data into the database
def insert_data(toll_booth_id, license_plate_text):
    query = """
        INSERT INTO OCRDetails (toll_booth_id, license_plate_text)
        VALUES (?, ?)
    """
    execute_query(query, (toll_booth_id, license_plate_text))

# Function to remove data from the database
def remove_data(toll_booth_id, license_plate_text):
    query = """
        DELETE FROM OCRDetails
        WHERE toll_booth_id = ? AND license_plate_text = ?
    """
    execute_query(query, (toll_booth_id, license_plate_text))

# Function to show all data from the OCRDetails table
def show_data():
    query = "SELECT * FROM OCRDetails"
    return execute_query(query, fetch=True)

# Example usage:
if __name__ == "__main__":
    # Insert data
    insert_data('TollBooth01', 'ABC1234')
    
    # Show all data
    data = show_data()
    for row in data:
        print(row)

    # Remove data
    remove_data('TollBooth01', 'ABC1234')
