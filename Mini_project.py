import gradio as gr
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'library_admin',
    'password': 'library123',
    'database': 'library_management_system'
}

# Database Connection Helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Database Query Functions
def execute_query(query, params=None, fetch=True):
    """Execute a query and return results"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            connection.commit()
            return True
    except Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def call_procedure(proc_name, params=None):
    """Call a stored procedure"""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.callproc(proc_name, params or ())
        
        # Fetch results if any
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
        
        connection.commit()
        return results
    except Error as e:
        print(f"Procedure error: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Dashboard Functions
def get_dashboard_stats():
    """Get dashboard statistics"""
    total_members_query = "SELECT COUNT(*) as count FROM Member"
    total_books_query = "SELECT COUNT(*) as count FROM Book"
    active_loans_query = "SELECT COUNT(*) as count FROM Transaction WHERE return_date IS NULL"
    pending_requests_query = "SELECT COUNT(*) as count FROM BorrowRequest WHERE status = 'Pending'"
    
    total_members = execute_query(total_members_query)[0]['count']
    total_books = execute_query(total_books_query)[0]['count']
    active_loans = execute_query(active_loans_query)[0]['count']
    pending_requests = execute_query(pending_requests_query)[0]['count']
    
    return total_members, total_books, active_loans, pending_requests

# Member Functions
def get_all_members():
    """Retrieve all members from database"""
    query = """
        SELECT member_id as 'Member ID', name as 'Name', email as 'Email', 
               phone as 'Phone', join_date as 'Join Date', strike_count as 'Strikes'
        FROM Member
        ORDER BY member_id
    """
    results = execute_query(query)
    return pd.DataFrame(results) if results else pd.DataFrame()

def search_members(search_term):
    """Search members by name, email, or ID"""
    if not search_term:
        return get_all_members()
    
    query = """
        SELECT member_id as 'Member ID', name as 'Name', email as 'Email', 
               phone as 'Phone', join_date as 'Join Date', strike_count as 'Strikes'
        FROM Member
        WHERE member_id LIKE %s OR name LIKE %s OR email LIKE %s
        ORDER BY member_id
    """
    search_pattern = f"%{search_term}%"
    results = execute_query(query, (search_pattern, search_pattern, search_pattern))
    return pd.DataFrame(results) if results else pd.DataFrame()

def add_member(member_id, name, email, phone):
    """Add a new member to the database"""
    if not all([member_id, name, email, phone]):
        return "Please fill all fields", get_all_members(), "", "", "", ""
    
    query = """
        INSERT INTO Member (member_id, name, phone, email, join_date, strike_count)
        VALUES (%s, %s, %s, %s, CURDATE(), 0)
    """
    result = execute_query(query, (member_id, name, phone, email), fetch=False)
    
    if result:
        return f"Added member: {name}", get_all_members(), "", "", "", ""
    else:
        return "Error adding member (ID might already exist)", get_all_members(), member_id, name, email, phone

# Book Functions
def get_all_books():
    """Retrieve all books from database"""
    query = """
        SELECT book_id as 'Book ID', title as 'Title', author as 'Author', 
               edition as 'Edition', condition_val as 'Condition', status as 'Status'
        FROM Book
        ORDER BY book_id
    """
    results = execute_query(query)
    return pd.DataFrame(results) if results else pd.DataFrame()

def search_books(search_term):
    """Search books by title, author, or ID"""
    if not search_term:
        return get_all_books()
    
    query = """
        SELECT book_id as 'Book ID', title as 'Title', author as 'Author', 
               edition as 'Edition', condition_val as 'Condition', status as 'Status'
        FROM Book
        WHERE book_id LIKE %s OR title LIKE %s OR author LIKE %s
        ORDER BY book_id
    """
    search_pattern = f"%{search_term}%"
    results = execute_query(query, (search_pattern, search_pattern, search_pattern))
    return pd.DataFrame(results) if results else pd.DataFrame()

def add_book(book_id, title, author, edition, condition):
    """Add a new book to the database"""
    if not all([book_id, title, author]):
        return "Please fill required fields (Book ID, Title, Author)", get_all_books(), "", "", "", "", condition
    
    edition = edition or "First"
    condition = condition or "Good"
    
    query = """
        INSERT INTO Book (book_id, author, title, edition, condition_val, status, purchase_date)
        VALUES (%s, %s, %s, %s, %s, 'Available', CURDATE())
    """
    result = execute_query(query, (book_id, author, title, edition, condition), fetch=False)
    
    if result:
        return f"Added book: {title}", get_all_books(), "", "", "", "First", "Good"
    else:
        return "Error adding book (ID might already exist)", get_all_books(), book_id, title, author, edition, condition

def update_book_status(book_id, new_status):
    """Update book status"""
    if not book_id or not new_status:
        return "Please provide Book ID and Status", get_all_books()
    
    query = "UPDATE Book SET status = %s WHERE book_id = %s"
    result = execute_query(query, (new_status, book_id), fetch=False)
    
    if result:
        return f"Updated {book_id} status to {new_status}", get_all_books()
    else:
        return f"Error updating book status (Book ID might not exist)", get_all_books()

# Borrow Request Creation Functions
def create_borrow_request(member_id_requester, member_id_owner, book_id):
    """Create a new borrow request"""
    if not all([member_id_requester, member_id_owner, book_id]):
        return "Please fill all fields", get_member_requests(""), "", "", ""
    
    # Generate new request ID
    query = "SELECT COUNT(*) as count FROM BorrowRequest"
    result = execute_query(query)
    new_id_num = result[0]['count'] + 1
    request_id = f"BR{str(new_id_num).zfill(3)}"
    
    # Insert new request
    query = """
        INSERT INTO BorrowRequest (request_id, request_date, status, member_id_requester, member_id_owner, book_id)
        VALUES (%s, CURDATE(), 'Pending', %s, %s, %s)
    """
    result = execute_query(query, (request_id, member_id_requester, member_id_owner, book_id), fetch=False)
    
    if result:
        return f"Created request {request_id} for book {book_id}", get_member_requests(member_id_requester), "", "", ""
    else:
        return "Error creating request (Check Member IDs and Book ID exist)", get_member_requests(member_id_requester), member_id_requester, member_id_owner, book_id

def get_member_requests(member_id):
    """Get all requests for a specific member"""
    if not member_id:
        return pd.DataFrame()
    
    query = """
        SELECT 
            br.request_id as 'Request ID',
            b.title as 'Book Title',
            br.book_id as 'Book ID',
            br.request_date as 'Request Date',
            br.status as 'Status',
            CASE 
                WHEN br.status = 'Completed' THEN 
                    CONCAT('Approved - Txn: ', t.transaction_id)
                WHEN br.status = 'Pending' THEN 'Waiting for approval'
                ELSE 'Request denied'
            END as 'Details'
        FROM BorrowRequest br
        JOIN Book b ON br.book_id = b.book_id
        LEFT JOIN Transaction t ON t.request_id = br.request_id
        WHERE br.member_id_requester = %s
        ORDER BY br.request_date DESC
    """
    results = execute_query(query, (member_id,))
    return pd.DataFrame(results) if results else pd.DataFrame()

def get_available_books_for_request():
    """Get books available for borrowing"""
    query = """
        SELECT book_id as 'Book ID', title as 'Title', author as 'Author', 
               edition as 'Edition', condition_val as 'Condition'
        FROM Book
        WHERE status = 'Available'
        ORDER BY title
    """
    results = execute_query(query)
    return pd.DataFrame(results) if results else pd.DataFrame()

# Strike Management Functions
def get_all_strikes():
    """Get all strikes with member and transaction details"""
    query = """
        SELECT 
            s.strike_id as 'Strike ID',
            s.member_id as 'Member ID',
            m.name as 'Member Name',
            s.transaction_id as 'Transaction ID',
            s.strike_date as 'Strike Date',
            s.reason as 'Reason'
        FROM Strike s
        JOIN Member m ON s.member_id = m.member_id
        ORDER BY s.strike_date DESC
    """
    results = execute_query(query)
    return pd.DataFrame(results) if results else pd.DataFrame()

# Borrow Request Functions (Admin)
def get_prioritized_requests(book_id):
    """Get prioritized borrow requests for a book"""
    results = call_procedure('GetPrioritizedRequestList', (book_id,))
    
    if not results:
        return pd.DataFrame(columns=["Priority", "Request ID", "Member", "Strikes", "Requested Date", "Member Since"])
    
    data = []
    for i, req in enumerate(results, 1):
        data.append({
            "Priority": i,
            "Request ID": req['request_id'],
            "Member": f"{req['requester_name']} ({req['member_id']})",
            "Strikes": req['strike_count'],
            "Requested Date": req['request_date'],
            "Member Since": req['join_date']
        })
    return pd.DataFrame(data)

def get_all_pending_requests():
    """Get all pending borrow requests grouped by book"""
    query = """
        SELECT DISTINCT br.book_id, b.title, b.author,
               (SELECT COUNT(*) FROM BorrowRequest WHERE book_id = br.book_id AND status = 'Pending') as pending_count
        FROM BorrowRequest br
        JOIN Book b ON br.book_id = b.book_id
        WHERE br.status = 'Pending'
        ORDER BY br.book_id
    """
    results = execute_query(query)
    return results if results else []

def approve_request(request_id, custom_due_date=None):
    """Approve a borrow request with optional custom due date"""
    if not request_id:
        return "Please enter a Request ID", None, ""
    
    # If custom due date is provided, we need to use a modified procedure
    if custom_due_date:
        # First, call the normal approval
        results = call_procedure('ApproveBorrowRequest', (request_id, 'A001'))
        
        if results is not None:
            # Then update the due date
            connection = get_db_connection()
            if connection:
                try:
                    cursor = connection.cursor()
                    # Get the transaction_id for this request
                    cursor.execute("SELECT transaction_id FROM Transaction WHERE request_id = %s", (request_id,))
                    result = cursor.fetchone()
                    
                    if result:
                        transaction_id = result[0]
                        # Update the due date
                        cursor.execute(
                            "UPDATE Transaction SET due_date = %s WHERE transaction_id = %s",
                            (custom_due_date, transaction_id)
                        )
                        connection.commit()
                        return f"Approved request: {request_id} with due date: {custom_due_date}", None, ""
                    else:
                        return f"Approved request: {request_id} (default 14 days)", None, ""
                except Error as e:
                    print(f"Error updating due date: {e}")
                    return f"Approved request: {request_id} (default 14 days)", None, ""
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()
            else:
                return f"Approved request: {request_id} (default 14 days)", None, ""
        else:
            return f"Error approving request {request_id}", None, ""
    else:
        # Use default 14-day period
        results = call_procedure('ApproveBorrowRequest', (request_id, 'A001'))
        
        if results is not None:
            return f"Approved request: {request_id} (default 14 days)", None, ""
        else:
            return f"Error approving request {request_id}", None, ""

def deny_request(request_id):
    """Deny a borrow request"""
    if not request_id:
        return "Please enter a Request ID", None
    
    results = call_procedure('DenyBorrowRequest', (request_id,))
    
    if results is not None:
        return f"Denied request: {request_id}", None
    else:
        return f"Error denying request {request_id}", None

# Active Loans Functions
def get_active_loans():
    """Get all active loans with status"""
    query = """
        SELECT 
            t.transaction_id as 'Transaction ID',
            b.title as 'Book',
            b.book_id as 'Book ID',
            m.name as 'Member',
            m.member_id as 'Member ID',
            t.borrow_date as 'Borrow Date',
            t.due_date as 'Due Date',
            CASE 
                WHEN t.due_date < CURDATE() THEN CONCAT('Overdue (', DATEDIFF(CURDATE(), t.due_date), ' days)')
                WHEN DATEDIFF(t.due_date, CURDATE()) <= 2 THEN CONCAT('Due in ', DATEDIFF(t.due_date, CURDATE()), ' days')
                ELSE 'Active'
            END as 'Status'
        FROM Transaction t
        JOIN BorrowRequest br ON t.request_id = br.request_id
        JOIN Book b ON br.book_id = b.book_id
        JOIN Member m ON br.member_id_requester = m.member_id
        WHERE t.return_date IS NULL
        ORDER BY t.due_date ASC
    """
    results = execute_query(query)
    if results:
        df = pd.DataFrame(results)
        return df
    return pd.DataFrame(columns=['Transaction ID', 'Book', 'Book ID', 'Member', 'Member ID', 'Borrow Date', 'Due Date', 'Status'])

def process_return(transaction_id):
    """Process a book return"""
    if not transaction_id:
        return "Please enter a Transaction ID", get_active_loans()
    
    query = """
        UPDATE Transaction
        SET return_date = CURDATE()
        WHERE transaction_id = %s AND return_date IS NULL
    """
    result = execute_query(query, (transaction_id,), fetch=False)
    
    if result:
        return f"Processed return for transaction: {transaction_id}", get_active_loans()
    else:
        return f"Transaction ID not found or already returned", get_active_loans()

# Gradio Interface
with gr.Blocks(title="Library Management System", theme=gr.themes.Soft(primary_hue="violet")) as demo:
    gr.Markdown("# Library Management System")
    gr.Markdown("### Admin Dashboard - Connected to MySQL Database")
    
    with gr.Tabs() as tabs:
        # Dashboard Tab
        with gr.Tab("Dashboard"):
            gr.Markdown("## Dashboard")
            gr.Markdown("Overview of your library management system")
            
            with gr.Row():
                total_members_display = gr.Number(label="Total Members", interactive=False)
                total_books_display = gr.Number(label="Total Books", interactive=False)
                active_loans_display = gr.Number(label="Active Loans", interactive=False)
                pending_requests_display = gr.Number(label="Pending Requests", interactive=False)
            
            refresh_dashboard_btn = gr.Button("Refresh Dashboard", variant="primary")
            
            def refresh_dashboard():
                stats = get_dashboard_stats()
                return stats[0], stats[1], stats[2], stats[3]
            
            refresh_dashboard_btn.click(
                refresh_dashboard,
                outputs=[total_members_display, total_books_display, active_loans_display, pending_requests_display]
            )
            
            gr.Markdown("### Quick Actions")
            gr.Markdown("Use the tabs above to manage members, books, process borrow requests, and handle returns.")
            
            # Load initial stats
            demo.load(refresh_dashboard, outputs=[total_members_display, total_books_display, active_loans_display, pending_requests_display])
        
        # Members Tab
        with gr.Tab("Members"):
            gr.Markdown("## Member Management")
            gr.Markdown("Manage library members and their information")
            
            with gr.Row():
                member_search = gr.Textbox(label="Search members by name, email, or ID...", scale=4)
                refresh_members_btn = gr.Button("Refresh", scale=1)
            
            members_table = gr.Dataframe(
                label="Members List", 
                interactive=False,
                wrap=True,
                column_widths=["15%", "20%", "25%", "15%", "15%", "10%"]
            )
            
            with gr.Accordion("Add New Member", open=False):
                with gr.Row():
                    new_member_id = gr.Textbox(label="Member ID (e.g., M013)")
                    new_member_name = gr.Textbox(label="Name")
                with gr.Row():
                    new_member_email = gr.Textbox(label="Email")
                    new_member_phone = gr.Textbox(label="Phone")
                submit_member = gr.Button("Add Member", variant="primary")
                member_status = gr.Textbox(label="Status", interactive=False)
            
            # Load initial data
            demo.load(lambda: get_all_members(), outputs=members_table)
            
            member_search.change(search_members, inputs=[member_search], outputs=[members_table])
            refresh_members_btn.click(lambda: get_all_members(), outputs=[members_table])
            submit_member.click(
                add_member, 
                inputs=[new_member_id, new_member_name, new_member_email, new_member_phone], 
                outputs=[member_status, members_table, new_member_id, new_member_name, new_member_email, new_member_phone]
            )
        
        # Books Tab
        with gr.Tab("Books"):
            gr.Markdown("## Book Catalog")
            gr.Markdown("Manage your library's book collection")
            
            with gr.Row():
                book_search = gr.Textbox(label="Search books by title, author, or ID...", scale=4)
                refresh_books_btn = gr.Button("Refresh", scale=1)
            
            books_table = gr.Dataframe(
                label="Book Collection", 
                interactive=False,
                wrap=True,
                column_widths=["12%", "28%", "20%", "12%", "13%", "15%"]
            )
            
            with gr.Accordion("Add New Book", open=False):
                with gr.Row():
                    new_book_id = gr.Textbox(label="Book ID (e.g., B017)")
                    new_book_title = gr.Textbox(label="Title")
                with gr.Row():
                    new_book_author = gr.Textbox(label="Author")
                    new_book_edition = gr.Textbox(label="Edition", value="First")
                new_book_condition = gr.Dropdown(label="Condition", choices=["Excellent", "Good", "Fair", "Poor"], value="Good")
                submit_book = gr.Button("Add Book", variant="primary")
                book_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Accordion("Update Book Status", open=False):
                gr.Markdown("**Change a book's availability status**")
                with gr.Row():
                    update_book_id = gr.Textbox(label="Book ID", placeholder="e.g., B001")
                    update_book_status_dropdown = gr.Dropdown(
                        label="New Status", 
                        choices=["Available", "Lent", "Reserved", "Maintenance"],
                        value="Available"
                    )
                update_status_btn = gr.Button("Update Status", variant="secondary")
                update_status_message = gr.Textbox(label="Status", interactive=False)
            
            # Load initial data
            demo.load(lambda: get_all_books(), outputs=books_table)
            
            book_search.change(search_books, inputs=[book_search], outputs=[books_table])
            refresh_books_btn.click(lambda: get_all_books(), outputs=[books_table])
            submit_book.click(
                add_book, 
                inputs=[new_book_id, new_book_title, new_book_author, new_book_edition, new_book_condition], 
                outputs=[book_status, books_table, new_book_id, new_book_title, new_book_author, new_book_edition, new_book_condition]
            )
            update_status_btn.click(update_book_status, inputs=[update_book_id, update_book_status_dropdown], outputs=[update_status_message, books_table])
        
        # Request Book Tab (Member Side)
        with gr.Tab("Request Book"):
            gr.Markdown("## Request a Book")
            gr.Markdown("Members can request to borrow available books")
            
            with gr.Row():
                gr.Markdown("### Step 1: View Available Books")
            
            refresh_available_books = gr.Button("Refresh Available Books")
            available_books_table = gr.Dataframe(label="Available Books", interactive=False)
            
            with gr.Row():
                gr.Markdown("### Step 2: Create Borrow Request")
            
            with gr.Row():
                req_member_id = gr.Textbox(label="Your Member ID (Requester)", placeholder="e.g., M001")
                req_owner_id = gr.Textbox(label="Owner Member ID", placeholder="e.g., M002", value="M001")
            
            req_book_id = gr.Textbox(label="Book ID to Request", placeholder="e.g., B001")
            
            gr.Markdown("**Note:** Owner ID is typically an admin/staff member ID (default: M001)")
            
            create_request_btn = gr.Button("Submit Request", variant="primary")
            request_create_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Row():
                gr.Markdown("### Step 3: View Your Requests")
            
            view_requests_member_id = gr.Textbox(label="Enter Your Member ID", placeholder="e.g., M001")
            view_requests_btn = gr.Button("View My Requests")
            member_requests_table = gr.Dataframe(label="Your Borrow Requests", interactive=False)
            
            # Event handlers
            refresh_available_books.click(lambda: get_available_books_for_request(), outputs=[available_books_table])
            create_request_btn.click(
                create_borrow_request, 
                inputs=[req_member_id, req_owner_id, req_book_id], 
                outputs=[request_create_status, member_requests_table, req_member_id, req_owner_id, req_book_id]
            )
            view_requests_btn.click(
                get_member_requests,
                inputs=[view_requests_member_id],
                outputs=[member_requests_table]
            )
            
            # Load initial data
            demo.load(lambda: get_available_books_for_request(), outputs=[available_books_table])
        
        # Borrow Requests Tab (Admin)
        with gr.Tab("Borrow Requests"):
            gr.Markdown("## Borrow Requests")
            gr.Markdown("Review and process pending borrow requests (prioritized by strikes and seniority)")
            
            book_selector = gr.Dropdown(label="Select Book to View Requests", choices=[], interactive=True)
            refresh_requests_btn = gr.Button("Refresh Book List", variant="secondary")
            
            def load_books_with_requests():
                pending = get_all_pending_requests()
                if pending:
                    choices = [f"{book['title']} by {book['author']} ({book['book_id']}) - {book['pending_count']} pending" for book in pending]
                    return gr.Dropdown(choices=choices)
                return gr.Dropdown(choices=[])
            
            requests_table = gr.Dataframe(
                label="Priority Queue", 
                interactive=False,
                wrap=True,
                column_widths=["10%", "15%", "25%", "10%", "20%", "20%"]
            )
            
            gr.Markdown("### Approve or Deny Request")
            
            with gr.Row():
                request_id_input = gr.Textbox(label="Request ID (e.g., BR007)", scale=2)
                due_date_input = gr.Textbox(
                    label="Custom Due Date (Optional - YYYY-MM-DD)", 
                    placeholder="e.g., 2025-11-15 or leave empty for 14 days",
                    scale=2
                )
            
            gr.Markdown("**Tip:** Leave due date empty to use default 14-day loan period")
            
            with gr.Row():
                approve_btn = gr.Button("Approve", variant="primary")
                deny_btn = gr.Button("Deny", variant="stop")
            
            request_status = gr.Textbox(label="Status", interactive=False)
            
            def show_requests(book_selection):
                if not book_selection:
                    return pd.DataFrame()
                # Extract book_id from selection
                book_id = book_selection.split('(')[1].split(')')[0]
                return get_prioritized_requests(book_id)
            
            refresh_requests_btn.click(load_books_with_requests, outputs=[book_selector])
            book_selector.change(show_requests, inputs=[book_selector], outputs=[requests_table])
            
            approve_btn.click(approve_request, inputs=[request_id_input, due_date_input], outputs=[request_status, requests_table, due_date_input])
            deny_btn.click(deny_request, inputs=[request_id_input], outputs=[request_status, requests_table])
            
            # Load initial data
            demo.load(load_books_with_requests, outputs=[book_selector])
        
        # Active Loans Tab
        with gr.Tab("Active Loans"):
            gr.Markdown("## Active Loans")
            gr.Markdown("Process book returns and manage active transactions")
            
            gr.Markdown("Late returns will automatically issue strikes to members")
            
            refresh_loans_btn = gr.Button("Refresh Active Loans")
            loans_table = gr.Dataframe(
                label="Current Loans", 
                interactive=False,
                wrap=True,
                column_widths=["10%", "20%", "10%", "15%", "10%", "12%", "12%", "11%"]
            )
            
            with gr.Row():
                transaction_id_input = gr.Textbox(label="Transaction ID (e.g., T001)")
                process_return_btn = gr.Button("Process Return", variant="primary")
            
            return_status = gr.Textbox(label="Status", interactive=False)
            
            refresh_loans_btn.click(lambda: get_active_loans(), outputs=[loans_table])
            process_return_btn.click(process_return, inputs=[transaction_id_input], outputs=[return_status, loans_table])
            
            # Load initial data
            demo.load(lambda: get_active_loans(), outputs=[loans_table])
        
        # Strikes Tab
        with gr.Tab("Strikes"):
            gr.Markdown("## Strike History")
            gr.Markdown("View all issued strikes and their reasons")
            
            refresh_strikes_btn = gr.Button("Refresh Strikes")
            strikes_table = gr.Dataframe(label="All Strikes", interactive=False)
            
            gr.Markdown("### Strike Information")
            gr.Markdown("""
            - Strikes are automatically issued when books are returned late
            - Members with more strikes have lower priority in borrow request queues
            - Strike count is tracked in the Members tab
            """)
            
            refresh_strikes_btn.click(lambda: get_all_strikes(), outputs=[strikes_table])
            
            # Load initial data
            demo.load(lambda: get_all_strikes(), outputs=[strikes_table])

if __name__ == "__main__":
    demo.launch()