from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
import time 
import csv
from tkinter import filedialog 
from tkinter.filedialog import asksaveasfilename, askopenfilename
import os
import seaborn
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import hashlib
from fpdf import FPDF, XPos, YPos
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from collections import Counter
import win32print
import win32api
import tempfile
from tkinter import simpledialog
from pypdf import PdfWriter
import pyttsx3
from  pdf2docx import Converter




#================================== School portal Class ===================================
class School_Portal:
    #database connection to relative paths
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schoolDB.db")
    

    def create_logo_on_canvas(self):
        """Create a custom logo using Canvas"""
        # Create canvas for logo
        canvas = Canvas(
            self.root,
            width=180,
            height=180,
            bg='navy',
            bd=2,
            relief=RIDGE
        )
        canvas.grid(row=0, column=0, padx=60, pady=20, sticky=NW)

        
        #adjust position upwards
        y_offset = -10


        # centre position
        x, y = 90, 90 + y_offset

        # Draw school logo
        # Outer circle
        canvas.create_oval(20, 20 + y_offset, 160, 160 + y_offset, fill='navy', outline='white', width=2)
        # Inner circle
        canvas.create_oval(30, 30 + y_offset, 150, 150 + y_offset, fill='#1A1A40', outline='royalblue', width=2)
        
        # Draw an inverted open book symbol ABOVE the text
        book_y = y - 15  # Raise book above the EduDash text

        # Book base (spine) – inverted "V" shape
        canvas.create_line(x - 15, book_y - 10, x, book_y, fill='white', width=4)
        canvas.create_line(x, book_y, x + 15, book_y - 10, fill='white', width=4)


        canvas.create_text(
            x - 10, y,
            text="Aca",
            fill='white',
            font=('Helvetical', 18, 'italic bold'),
            anchor=E

        )
      
        canvas.create_text(
            x - 10, y,
            text="Dash",
            fill='#FF6F61',
            font=('Helvetical', 18, 'italic bold'),
            anchor=W

        )
        
        # System name under ovals
        canvas.create_text(
            x, 170 + y_offset,  # Positioned below the inner circle
            text="Your  smart",
            fill='white',
            font=('lato', 10, 'bold italic'),
           
        )
        canvas.create_text(
            x, 185 + y_offset,  # Further down
            text="academic dashboard",
            fill='#FF6F61',
            font=('lato', 10, 'bold italic'),
            
        )

        return canvas
    
    # Add this method to your School_Portal class
    def get_embedded_icon(self):
        """Create and return the icon as a PhotoImage directly"""
        try:
            # Create icon image in memory
            icon_size = (32, 32)
            icon = Image.new('RGBA', icon_size, 'navy')
            draw = ImageDraw.Draw(icon)
            
            # Draw outer circle
            draw.ellipse([2, 2, 30, 30], outline='white', width=1)
            
            # Draw inner circle
            draw.ellipse([6, 6, 26, 26], fill='#1A1A40', outline='royalblue', width=1)
            
            # Add text
            try:
                font = ImageFont.truetype("inter.ttf", 8)
            except:
                font = ImageFont.load_default()
            
            # Draw "Aca" and "Dash" side by side, centered together
            text1 = "Aca"
            text2 = "Dash"

            # Get individual widths
            text1_size = draw.textbbox((0, 0), text1, font=font)
            text2_size = draw.textbbox((0, 0), text2, font=font)

            text1_width = text1_size[2] - text1_size[0]
            text2_width = text2_size[2] - text2_size[0]
            text_height = max(text1_size[3] - text1_size[1], text2_size[3] - text2_size[1])

            total_width = text1_width + text2_width
            start_x = (icon_size[0] - total_width) // 2
            text_y = (icon_size[1] - text_height) // 2

            # Draw texts
            draw.text((start_x, text_y), text1, fill='white', font=font)
            draw.text((start_x + text1_width, text_y), text2, fill='#FF6F61', font=font)


                # Convert to PhotoImage
            buffer = BytesIO()
            icon.save(buffer, format='PNG')
            return PhotoImage(data=base64.b64encode(buffer.getvalue()))
        except Exception as e:
            print(f"Error creating icon: {e}")
            return None
        

    def __init__(self, root):
        self.root = root
        root.config(bg="lavender")
        self.root.title("Academic Management Dashboard")
        self.engine = pyttsx3.init()
        

        # Initialize the current_user_role attribute
        self.current_user_role = None  # Default value before login
        self.logged_in_username = None
        self.user_assignments = None

        #self.create_user_table() 
        #self.create_assignment_table()
        self.create_selector_frame()
        self.setup_main_filter_frame()
        


            # Set custom icon using embedded method
        try:
            icon = self.get_embedded_icon()
            if icon:
                self.root.iconphoto(True, icon)  # True makes it the default icon
        except Exception as e:
            print(f"Could not load icon: {e}")
        

        # Create logo using canvas instead of image
        self.logo_canvas = self.create_logo_on_canvas()



       #======================= Table Title ===========================     
        self.label = Label(
            text=" Student Academic Records Portal ",
            bg='navy',
            font=('poppins', 18, 'bold'),
            fg='white',
            relief=SUNKEN,  # Added border relief
            bd=1,         # Added border width
            pady=5        # Added vertical padding within the label
        )
        self.label.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky=EW)

        # Configure grid layout
        self.configure_grid(root)
    
           

        #======================= Table Display ========================
        # Configure the Treeview style
        style = ttk.Style()
        style.configure("Treeview.Heading", foreground="dark blue", font=("inter", 10, "bold"))  # Set header text color and font
        style.configure("Treeview", rowheight=20, font=("inter", 10))
        style.map("Treeview", background=[("selected", "#3B3B3B")])

        # Create the Treeview
        self.tree = ttk.Treeview(
            height=10,  # Minimum number of rows
            columns=["", "", "", "", "", "", "", "", "", ""]
        )
        self.tree.grid(row=8, column=0, columnspan=2, padx=10, sticky=NSEW)  # Make treeview expandable

        # Add scrollbars to Treeview
        y_scrollbar = ttk.Scrollbar(orient=VERTICAL, command=self.tree.yview)
        y_scrollbar.grid(row=8, column=3, sticky=NS)
        self.tree.configure(yscrollcommand=y_scrollbar.set)


        # Define the column headers and their widths
        self.tree.heading("#0", text="ID")
        self.tree.column("#0", width=50)

        self.tree.heading("#1", text="First Name")
        self.tree.column("#1", width=90)

        self.tree.heading("#2", text="Last Name")
        self.tree.column("#2", width=120)

        self.tree.heading("#3", text="Gender")
        self.tree.column("#3", width=60)

        self.tree.heading("#4", text="Form")
        self.tree.column("#4", width=40)

        self.tree.heading("#5", text="Class")
        self.tree.column("#5", width=60)

        self.tree.heading("#6", text="Subject")
        self.tree.column("#6", width=100)

        self.tree.heading("#7", text="Class Score")
        self.tree.column("#7", width=85, stretch=FALSE)

        self.tree.heading("#8", text="Exam Score")
        self.tree.column("#8", width=85, stretch=FALSE)

        self.tree.heading("#9", text="Total Score")
        self.tree.column("#9", width=80, stretch=FALSE)

        self.tree.heading("#10", text="Grade & Remarks")
        self.tree.column("#10", width=120, stretch=FALSE)
                


        #======================= Time and Date ===========================

        def tick():
            d = datetime.datetime.now()
            today = "{:%B %d, %Y}".format(d)

            time2 = time.strftime('%I:%M:%S %p')
            self.lblInfo.config(text= time2+'\t'+today)
            self.lblInfo.after(200, tick)

        self.lblInfo = Label(font=('roboto mono', 16, 'bold'),bg='lavender' ,fg='dark blue', bd=5, relief= SUNKEN)
        self.lblInfo.grid(row=11, column=0, columnspan=2, sticky=N)
        tick()



        #======================= Digital Counter ===========================
        # Counter Label
        self.counter_label = Label(font=("fira mono", 16), fg="firebrick", bg="khaki", borderwidth=5, relief=SUNKEN)
        self.counter_label.grid(row=11, column=3, sticky=E) 
        
        self.counter_value = 0 

        self.digit_counter()
    
    def digit_counter(self):
        self.counter_value += 1
        self.counter_label.config(text=str(self.counter_value))
        self.counter_label.after(60000, self.digit_counter)  # Update every 60 seconds


    #======================= Message Display ========================
        self.message = Label(text="", fg="orange red", bg= 'lavender', font=('inter', 10, 'bold', 'italic'))
        self.message.grid(row=3, column=1, sticky=SW)
     
    #============================= Menu Function ==========================
    def create_menu_bar(self):
        """Create the application menu bar with role-based options"""
        chooser = Menu(self.root)
        self.root.config(menu=chooser)

        # File Menu
        file_menu = Menu(chooser, tearoff=0)
        chooser.add_cascade(label="File", menu=file_menu)

        # Role-specific file menu items
        if self.current_user_role == "admin":
            file_menu.add_command(label="Delete Record", command=self.dele)
            file_menu.add_command(label="Delete All Records", command=self.delete_all_records)
            file_menu.add_separator()
        elif self.current_user_role == "user":
            file_menu.add_command(label="Add Record", command=self.add_record_window)
            file_menu.add_command(label="Add from CSV", command=self.import_csv_data)
            file_menu.add_command(label="Edit Record", command=self.edit)
            file_menu.add_separator()
            file_menu.add_command(label="Export as CSV", command=self.export_csv_window)
        
            
        # Common file menu items
        file_menu.add_command(label="Export as Excel", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Show records", command=self.show_records_window)
        file_menu.add_command(label="Print Records", command=self.print_data)   
        if self.current_user_role == "admin":
            file_menu.add_command(label="Print Report", command=self.print_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.ex)
        
        tool_menu = Menu(chooser, tearoff=0)
        chooser.add_cascade(label="Tools", menu=tool_menu)
        tool_menu.add_command(label=" Convert PDF to Word", command=self.convert_pdf_docx)
        tool_menu.add_command(label="Merge PDF Files", command=self.merge_pdfs)
        tool_menu.add_separator()
        tool_menu.add_command(label="Calculator", command=self.calculator)
       

        # Admin-specific menus
        if self.current_user_role == "admin":
            manage_menu = Menu(chooser, tearoff=0)
            manage_menu.add_command(label="Add New User", command=self.sign_up)
            manage_menu.add_separator()
            manage_menu.add_command(label="Assign Classes & Subjects", command=self.assign_class_subject)
            manage_menu.add_command(label="Delete Assignment", command=self.open_delete_assignment_window)
            manage_menu.add_separator()
            manage_menu.add_command(label="Find Teacher Assignment", command=self.open_search_teacher_window)
            chooser.add_cascade(label="Manage User", menu=manage_menu) 

        # Common menus for all roles
        search_menu = Menu(chooser, tearoff=0)
        search_menu.add_command(label="Search Record", command=self.search_record)
        chooser.add_cascade(label="Search", menu=search_menu)
        
       
        #student_records_menu.add_command(label="Edit Year/Period", command=self.open_edit_year_period_window)
        
        # Add Stats Menu
        stats_menu = Menu(chooser, tearoff=0)
        stats_menu.add_command(label="Class Statistics", command=self.show_class_stats)
        chooser.add_cascade(label="Stats", menu=stats_menu)

        # Add to your create_menu_bar method
        home_menu = Menu(chooser, tearoff=0)
        home_menu.add_command(label="Reset to Home", command=self.reset_to_home)
        chooser.add_cascade(label="Home", menu=home_menu)

        about_menu = Menu(chooser, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        chooser.add_cascade(label="Help", menu=about_menu)

        password_menu = Menu(chooser, tearoff=0)
        password_menu.add_command(label="Change Password", command=self.change_password)
        chooser.add_cascade(label="Password", menu=password_menu)

        logout_menu = Menu(chooser, tearoff=0)
        logout_menu.add_command(label="Logout", command=self.logout)
        chooser.add_cascade(label="Logout", menu=logout_menu)


    #=======================  Run Query ===========================
    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    # ================================= Setup method===========================
    def setup_ui(self):
        """Setup all UI elements after database connection"""
        # Configure grid
        self.configure_grid(self.root)
        
        # Create main UI elements
        self.create_title_label()
        self.create_treeview()
        self.create_time_display()
        self.create_counter()
        self.create_class_selector()
        self.create_menu_bar()
        self.create_message_display()
        
        # Load initial records
        self.view_records()

    def configure_grid(self, root):
        """Configure the grid layout for the root window."""
        # Configure rows and columns to be expandable
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)

    
     #========================= Function Decorators =========================

     #======================= Role-based Access Control =========================
    def require_role(*roles):
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                if self.current_user_role not in roles:
                    self.show_message("Access Denied", f"Only {', '.join(roles)}s can perform this action.", "warning")
                    return
                return func(self, *args, **kwargs)
            return wrapper
        return decorator  

    #=======================Error Handler ===========================     
    def db_error_handler(func):
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.show_message("Error", f"An error occurred: {e}", "error")
        return wrapper
    
    #=============================== Clear Treeview =========================
    def clear_treeview(func):
        def wrapper(self, *args, **kwargs):
            for item in self.tree.get_children():
                self.tree.delete(item)
            return func(self, *args, **kwargs)
        return wrapper
    
    
  #======================================== View Records =========================================
    @clear_treeview
    def view_records(self):
        """View all records in the Treeview"""
        query = "SELECT * FROM Students_records ORDER BY totalScore DESC"
        db_table = self.run_query(query)
        if db_table is None:  # Add this check
            return
        for data in db_table:
            self.tree.insert("", 1000, text=data[0], values=(data[1:]))



   #=======================  Delete Single  Record ===========================
    @db_error_handler
    @require_role("admin")
    def delete_record(self):
        """Delete a single record (admin only)"""
        
        self.tree.item(self.tree.selection())["values"][1]
        
        self.message["text"] = ""
        number = self.tree.item(self.tree.selection())["text"]
        query = "DELETE FROM students_records WHERE id = ?"
        self.run_query(query, (number, ))
        self.show_message("Success" ,"Record {} deleted suctcessfully!".format(number), "success")

        self.view_records()

    def dele(self):
        de = messagebox.askquestion("Delete Record", "Do you want to delete a record")
        if de == "yes":
            self.delete_record()


    #================================ Delete all records ========================
    @db_error_handler
    @require_role("admin")
    def delete_all_records(self):
        """Delete a single record (admin only)"""
               # Confirm the action with the user
        confirm = messagebox.askquestion("Delete All Records", "Are you sure you want to delete all records? This action cannot be undone.")
        if confirm == "yes":
            # SQL query to delete all records
            query = "DELETE FROM students_records"
            self.run_query(query)  # Execute the query
            self.show_message("Success","All records have been deleted successfully.","success")
            
            self.view_records()  # Refresh the Treeview to reflect the changes
        
  
       
    #======================== Reset to State =========================
    @db_error_handler
    def reset_to_home(self):
        """Reset the application to its default state without showing all records"""
        # Clear class and subject selections
        self.class_combobox.set("Choose Class")
        self.subject_combobox.set("Choose Subject")

        # Clear the Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Clear any graphs
        for widget in self.root.grid_slaves(column=2):  # Clear column 2 (graphs)
            widget.destroy()

        # Clear existing widgets
        for widget in self.root.grid_slaves(row=0, column=1):
            widget.destroy()
        
        # Reset the message display
        self.message["text"] = ""

        # Reset percentage display if it exists
        if hasattr(self, 'percentage_label'):
            self.percentage_label.config(text="")

        # Reset window size
        self.adjust_window_size()

        # Display success message
        self.show_message("Success", "Application reset to home state.", "success")

     #=============================== Add New Record =======================================
    @require_role("user")
    def add_record_window(self):
        """Open a Toplevel window to add a new record"""
        add_window = Toplevel(self.root)
        add_window.title("Add New Record")
        add_window.geometry("400x400")
        add_window.config(bg="#3B3B3B")
        add_window.resizable(False, False)  # Prevent resizing
    

        # Center the window
        self.center_window(add_window)
        add_window.transient(self.root)
        add_window.grab_set()  # Make the new window modal
        

        # Add form fields
        Label(add_window, text="First Name:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky=W)
        firstname_entry = Entry(add_window, width=30)
        firstname_entry.grid(row=0, column=1, padx=10, pady=5)

        Label(add_window, text="Last Name:", bg='#3B3B3B', fg='lavender', font=(' inter', 10, 'bold')).grid(row=1, column=0, padx=10, pady=5, sticky=W)
        lastname_entry = Entry(add_window, width=30)
        lastname_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(add_window, text="Gender:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky=W)
        gender_combobox = ttk.Combobox(add_window, width=27, state="readonly")
        gender_combobox['values'] = ('F', 'M')
        gender_combobox.grid(row=2, column=1, padx=10, pady=5)
        gender_combobox.set("Choose Gender")

        Label(add_window, text="Form:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=3, column=0, padx=10, pady=5, sticky=W)
        form_combobox = ttk.Combobox(add_window, width=27, state="readonly")
        form_combobox['values'] = (1, 2, 3)
        form_combobox.grid(row=3, column=1, padx=10, pady=5)
        form_combobox.set("Choose Form")

        Label(add_window, text="Class:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=4, column=0, padx=10, pady=5, sticky=W)
        class_combobox = ttk.Combobox(add_window, width=27, state="readonly")
        class_combobox.grid(row=4, column=1, padx=10, pady=5)

        Label(add_window, text="Subject:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=5, column=0, padx=10, pady=5, sticky=W)
        subject_combobox = ttk.Combobox(add_window, width=27, state="readonly")
        subject_combobox.grid(row=5, column=1, padx=10, pady=5)
        
        #Populate the comboboxes with values base on user role
        self.populate_class_subject_comboboxes(class_combobox, subject_combobox)
        # In add_record_window method:
        vcd = (self.root.register(lambda x: self.validate_score(x, 30, "Class Score")), '%P')
        Label(add_window, text="Class Score (30%):", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=6, column=0, padx=10, pady=5, sticky=W)
        class_score_entry = Entry(add_window, validate='key', validatecommand=vcd, width=30)
        class_score_entry.grid(row=6, column=1, padx=10, pady=5)

        vcd1 = (self.root.register(lambda x: self.validate_score(x, 70, "Exam Score")), '%P')
        Label(add_window, text="Exam Score (70%):", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=7, column=0, padx=10, pady=5, sticky=W)
        exam_score_entry = Entry(add_window, validate='key', validatecommand=vcd1, width=30)
        exam_score_entry.grid(row=7, column=1, padx=10, pady=5)

        Label(add_window, text="Academic Year:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=8, column=0, padx=10, pady=5, sticky=W)
        year_entry = Entry(add_window, width=30)
        year_entry.insert(0, "E.g. 2024/2025")  # optional default
        year_entry.grid(row=8, column=1, padx=10, pady=5)

        periods_list =["Sem1", "Sem2", "Term1", "Term2", "Term3"]
        Label(add_window, text="Period:", bg='#3B3B3B', fg='lavender', font=('inter', 10, 'bold')).grid(row=9, column=0, padx=10, pady=5, sticky=W)
        period_cbox = ttk.Combobox(add_window, values=periods_list, width=27, state="readonly")
        period_cbox.grid(row=9, column=1, padx=10, pady=5)
        period_cbox.set("E.g. Sem1 or Term 1")

        
        # Add Record Button
        Button(
            add_window,
            text="Add Record",
            command=lambda: self.add_record_from_window(
                firstname_entry.get(),
                lastname_entry.get(),
                gender_combobox.get(),
                form_combobox.get(),
                class_combobox.get(),
                subject_combobox.get(),
                class_score_entry.get(),
                exam_score_entry.get(),
                year_entry.get(),
                period_cbox.get(),
                add_window
            ),
            bg="green",
            fg="white",
            font=("inter", 10, "bold")
        ).grid(row=10, column=1, pady=20, sticky=E)

    # Validation functions for numeric inputs
    
    def validate_score(self, new_value, max_score, score_type=""):
            """
            Validate numeric input for scores with a maximum limit.
            
            Args:
                new_value (str): The value to validate
                max_score (int): Maximum allowed score (30 for class score, 70 for exam score)
                score_type (str): Type of score being validated (for error message)
            
            Returns:
                bool: True if valid, False otherwise
            """
            if not new_value:
                return True
                
            
            try:
                value = int(new_value)
                if value <= max_score:
                    return True
                else:
                    message = f" cannot exceed {max_score}"
                    if score_type:
                        message = f"{score_type} {message}"
                    self.show_message("Info",message, "info")
                    return False
            except ValueError:
                self.show_message("Info","Please enter numbers only", "info")
                return False
            
    #=============================== Add Record from Window =======================================
    @db_error_handler
    def add_record_from_window(self, fname, lname, gender, form, class_, subject, class_score, exam_score, year, period, window):
            # Validate inputs
        if not all([fname, lname, gender, form, class_, subject, class_score, exam_score, year, period]):
            self.show_message("Warning", "All fields are required", "warning")
            return

        # Calculate total score
        total_score = float(class_score) + float(exam_score)

        # Determine grade
        if 75 <= total_score <= 100:
            grade = "A1  Excellent"
        elif 70 <= total_score <= 74:
            grade = "B2  Very Good"
        elif 65 <= total_score <= 69:
            grade = "B3  Good"
        elif 60 <= total_score <= 64:
            grade = "C4  Credit"
        elif 55 <= total_score <= 59:
            grade = "C5  Credit"
        elif 50 <= total_score <= 54:
            grade = "C6  Credit"
        elif 45 <= total_score <= 49:
            grade = "D7  Pass"
        elif 40 <= total_score <= 44:
            grade = "E8  Pass"
        else:
            grade = "F9  Fail"

        # Insert student record
        insert_student = """
            INSERT INTO students_records
            (fname, lname, gender, form, class_, subject, classScore, examScore, totalScore, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (fname, lname, gender, form, class_, subject, float(class_score), float(exam_score), total_score, grade)
        self.run_query(insert_student, params)

        # Fetch student_id
        fetch_id = self.run_query("""
            SELECT id FROM students_records
            WHERE fname = ? AND lname = ? AND class_ = ?
            ORDER BY id DESC LIMIT 1
        """, (fname, lname, class_))
        result = fetch_id.fetchone()
        if not result:
            self.show_message("Error", "Could not retrieve student ID.", "error")
            return
        student_id = result[0]

        # Generate student_num
        prefix = lname[0].upper()
        latest = self.run_query("""
            SELECT student_num FROM academic_records
            WHERE student_num LIKE ?
            ORDER BY student_num DESC LIMIT 1
        """, (f"{prefix}%",))
        last_row = latest.fetchone()
        if last_row and last_row[0]:
            try:
                last_num = int(last_row[0][1:])
                student_num = f"{prefix}{last_num + 1:03d}"
            except:
                student_num = f"{prefix}001"
        else:
            student_num = f"{prefix}001"

        sch_code = "0040801"
        index_num = f"{sch_code}{student_num}"

        # Insert into academic_records
        self.run_query("""
            INSERT INTO academic_records (sch_code, student_num, index_num, student_id, year, period)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sch_code, student_num, index_num, student_id, year, period))

        # Call the function to update previous records if any
        self.update_academic_records_for_previous_entries(year, period)

        self.show_message("Success", f"Record for {fname} {lname} added successfully!", "success")
            
            # Refresh the Treeview
        self.view_records()

            # Close the Toplevel window
        window.destroy()


     #=======================  Edit Record ===========================
    @require_role("user")
    def edit_box(self):
        """Open a window to edit the selected record (user only)"""
        self.message["text"] = ""
        try:
            # Get the selected record? values
            selected_item = self.tree.selection()
            if not selected_item:
                raise IndexError("No record selected")
            record_values = self.tree.item(selected_item)["values"]
            record_id = self.tree.item(selected_item)["text"]  
        except IndexError:
            self.show_message("Info","Please select a record to edit", "info")
            
            return
        # Get the selected record? values
        selected_item = self.tree.selection()
        if not selected_item:
            raise IndexError("No record selected")
        record_values = self.tree.item(selected_item)["values"]
        record_id = self.tree.item(selected_item)["text"]  # Assuming ID is stored in the Treeview? text field
        
        # Open the edit window
        self.edit_wind = Toplevel()
        self.edit_wind.title("Edit Record")
        self.edit_wind.geometry("350x400")
        self.edit_wind.config(bg="lavender")
        self.edit_wind.grab_set()

        # Field labels and entry fields
        fields = [
            ("First Name", record_values[0]),
            ("Last Name", record_values[1]),
            ("Gender", record_values[2]),
            ("Form", record_values[3]),
            ("Class", record_values[4]),
            ("Subject", record_values[5]),
            ("Class Score", record_values[6]),
            ("Exam Score", record_values[7]),
            ("Total Score", record_values[8]),
            ("Grade", record_values[9]),
        ]

        # Store entry widgets for later retrieval
        self.edit_entries = {}

        for i, (label_text, value) in enumerate(fields):
            Label(self.edit_wind, text=label_text + ":", font=("inter", 12), bg="lavender").grid(row=i, column=0, padx=10, pady=5, sticky=W)
            entry = Entry(self.edit_wind, width=30)
            entry.insert(0, value)  # Pre-fill with the current value
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.edit_entries[label_text] = entry

        # Save Changes Button
        Button(
            self.edit_wind,
            text="Save Changes",
            command=lambda: self.save_changes(record_id),
            bg="green",
            fg="white",
            font=("inter", 10, "bold")
        ).grid(row=len(fields), column=1, pady=20, sticky=E)


    #==================================== Save Changes / Update Changes  ======================================================
    @db_error_handler
    @require_role("user")
    def save_changes(self, record_id):
        """Save the changes made to the record"""
        # Retrieve updated values from the entry fields
        updated_values = {field: entry.get() for field, entry in self.edit_entries.items()}

        # Validate that all fields are filled
        if any(not value.strip() for value in updated_values.values()):
            self.show_message("Warnibg", "All fields are required.", "Warning")
            return

        # Update the database
        query = """
            UPDATE students_records 
            SET fname=?, lname=?, gender=?, form=?, class_=?, subject=?, classScore=?, examScore=?, totalScore=?, grade=? 
            WHERE id=?
        """
        parameters = (
            updated_values["First Name"],
            updated_values["Last Name"],
            updated_values["Gender"],
            updated_values["Form"],
            updated_values["Class"],
            updated_values["Subject"],
            updated_values["Class Score"],
            updated_values["Exam Score"],
            updated_values["Total Score"],
            updated_values["Grade"],
            record_id
        )
        self.run_query(query, parameters)

        # Close the edit window and refresh the records
        self.edit_wind.destroy()
        self.show_message("Success",f"Record {record_id} updated successfully.", "success")
        self.view_records()

   #=================================================== Edit, Help, Exit Functions ==================================================
    @require_role("user")
    def edit(self):
        ed = messagebox.askquestion("Edit Record", "Do you want to Edit a record")
        if ed == "yes":
            self.edit_box()
    

    def ex(self): 
        exi = messagebox.askquestion("Exit Application", "Do you want to Close application")
        if exi == "yes":
            self.root.destroy()

     #========================================= Search Record =========================================
    # Add the search function to the School_Portal class
    @clear_treeview
    def search_record(self):
        def perform_search():
            try:
                # Get the search field and value
                search_field = search_field_var.get()
                search_value = search_value_var.get().strip()

                # Validate input
                if not search_field or search_field == "Choose Field":
                    self.show_message("info", "Please select a valid search field.", "info")
                    return
                if not search_value:
                    self.show_message("info", "Please enter a value to search.", "info")
                    return

                # Build the query dynamically based on the selected field
                query = f"SELECT * FROM students_records WHERE {search_field} LIKE ?"
                parameters = [f"%{search_value}%"]

                # Execute the query
                
                # Execute the query using PostgreSQL cursor
                
                records = self.run_query(query, parameters).fetchall()

                # Check if any records were found
                if not records:
                    self.show_message("No Results", "No records found matching the search criteria.", "info")
                    search_window.lift()  # Keep the search window on top
                    return

                # Display the results in the Treeview
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for record in records:
                    self.tree.insert("", "end", text=record[0], values=record[1:])

                # Close the search window
                search_window.destroy()

            except Exception as e:
                self.show_message("Error", f"An error occurred while searching: {e}", "error")



        # Create a Toplevel window for the search functionality
        search_window = Toplevel(self.root)
        search_window.title("Search Record")
        search_window.geometry("400x200")
        search_window.config(bg="#3B3B3B")
        search_window.grab_set()

        # Dropdown for selecting the search field
        search_field_var = StringVar(value="Choose Field")
        Label(search_window, text="Search By:", font=("inter", 12),fg="white", bg="#3B3B3B").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        search_field_dropdown = ttk.Combobox(search_window, textvariable=search_field_var, state="readonly", width=20)
        search_field_dropdown['values'] = ("id", "fname", "lname", "subject", "class_")  # Add more fields as needed
        search_field_dropdown.grid(row=0, column=1, padx=10, pady=10)

        # Entry for entering the search value
        search_value_var = StringVar()
        Label(search_window, text="Enter Value:", font=("inter", 12),fg="white", bg="#3B3B3B").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        search_value_entry = Entry(search_window, textvariable=search_value_var, width=25)
        search_value_entry.grid(row=1, column=1, padx=10, pady=10)

        # Search button
        Button(search_window, text="Search", command=perform_search, bg="green", fg="white", font=("inter", 10, "bold")).grid(row=2, column=1, pady=20, sticky=E)

    # Add the search function to the menu bar
    def add_search_to_menu(self):
        chooser = Menu(self.root)
        self.root.config(menu=chooser)

        # Add a "Search" option to the menu
        search_menu = Menu(chooser, tearoff=0)
        search_menu.add_command(label="Search Record", command=self.search_record)
        chooser.add_cascade(label="Search", menu=search_menu)
        
       
     #=============================== Import Records ===============================
    def calculate_grade(self, total_score):
        """Calculate grade based on total score"""
        if 75 <= total_score <= 100:
            return "A1  Excellent"
        elif 70 <= total_score <= 74:
            return "B2  Very Good"
        elif 65 <= total_score <= 69:
            return "B3  Good"
        elif 60 <= total_score <= 64:
            return "C4  Credit"
        elif 55 <= total_score <= 59:
            return "C5  Credit"
        elif 50 <= total_score <= 54:
            return "C6  Credit"
        elif 45 <= total_score <= 49:
            return "D7  Pass"
        elif 40 <= total_score <= 44:
            return "E8  Pass"
        else:
            return "F9  Fail"
        
     #========================================================== ===================================================
    @db_error_handler
    def get_or_create_student_identity(self, fname, lname, gender, form, class_, year, period):
        # Find student in students_records
        result = self.run_query("""
            SELECT id FROM students_records
            WHERE fname = ? AND lname = ? AND class_ = ?
            ORDER BY id DESC LIMIT 1
        """, (fname, lname, class_)).fetchone()

        if not result:
            return None  # Don't insert student here

        student_id = result[0]

        # Check for existing academic record
        academic = self.run_query("""
            SELECT id FROM academic_records
            WHERE student_id = ? AND year = ? AND period = ?
        """, (student_id, year, period)).fetchone()

        if not academic:
            # Generate student_num
            prefix = lname[0].upper()
            last_entry = self.run_query("""
                SELECT student_num FROM academic_records
                WHERE student_num LIKE ?
                ORDER BY student_num DESC LIMIT 1
            """, (f"{prefix}%",)).fetchone()

            last_num = int(last_entry[0][1:]) if last_entry else 0
            student_num = f"{prefix}{last_num + 1:03d}"
            index_num = f"0040801{student_num}"

            self.run_query("""
                INSERT INTO academic_records (sch_code, student_num, index_num, student_id, year, period)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("0040801", student_num, index_num, student_id, year, period))

        return student_id

    @db_error_handler
    def add_record_from_import(self, fname, lname, gender, form, class_, subject, class_score, exam_score, year, period):
        total_score = float(class_score) + float(exam_score)
        grade = self.calculate_grade(total_score)

        # Check if record exists
        existing = self.run_query("""
            SELECT id FROM students_records 
            WHERE fname = ? AND lname = ? AND class_ = ? AND subject = ?
        """, (fname, lname, class_, subject)).fetchone()

        if existing:
            self.run_query("""
                UPDATE students_records 
                SET gender=?, form=?, classScore=?, examScore=?, totalScore=?, grade=? 
                WHERE id=?
            """, (gender, form, class_score, exam_score, total_score, grade, existing[0]))
            return existing[0]

        # Insert new record
        self.run_query("""
            INSERT INTO students_records
            (fname, lname, gender, form, class_, subject, classScore, examScore, totalScore, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fname, lname, gender, form, class_, subject, class_score, exam_score, total_score, grade))

        return self.run_query("SELECT last_insert_rowid()").fetchone()[0]

    @db_error_handler
    @require_role("user")
    def import_csv_data(self):
        """Import student records from a CSV file"""
        # Show information dialog about required fields
        info_message = """
        CSV File Requirements:

        Required Columns:
        1. fname (First Name)
        2. lname (Last Name)
        3. gender (M/F)
        4. form (1/2/3)
        5. class_ (e.g., 1Sci1, 2Arts1)
        6. subject (e.g., Mathematics, English)
        7. classScore (0-30)
        8. examScore (0-70)
        9. year e.g. 2024/2025
        10. period e.g. Term1 or Sem1

        Notes:
        • Header row must be present
        • All columns are required
        • Class Score must be between 0-30
        • Exam Score must be between 0-70
        • Total Score and Grade will be calculated automatically
        
        Example CSV format:
        fname,lname,gender,form,class_,subject,classScore,examScore,year,period
        John,Doe,M,1,1Sci1,Physics,25,60,2024/2025,Term1
        Jane,Smith,F,2,2Arts1,English,28,65,2025/2026,Sem1
        """
        
        messagebox.showinfo("Import Requirements", info_message)

    
        # File dialog to select CSV file
        file_path = filedialog.askopenfilename(
            title="Select CSV File to Import",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return

        # Read CSV file and validate structure
        with open(file_path, 'r',encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            
            # Define required columns
            required_columns = [
                'fname', 'lname', 'gender', 'form', 'class_', 
                'subject', 'classScore', 'examScore', 'year', 'period'
            ]
            
            # Validate CSV structure
            csv_columns = csv_reader.fieldnames
            if not csv_columns:
                self.show_message("Error", "CSV file is empty or improperly formatted.", "error")
                return

            missing_columns = [col for col in required_columns if col not in csv_columns]
            if missing_columns:
                self.show_message(
                    "Error",
                    f"Missing columns: {', '.join(missing_columns)}\nRequired columns: {', '.join(required_columns)}",
                    "error"
                )
                return

            # Initialize counters
            records_processed = 0
            records_imported = 0
            records_updated = 0
            errors = []

            # Process each row
            for row_num, row in enumerate(csv_reader, start=2):
                    class_score = float(row['classScore'].strip())
                    exam_score = float(row['examScore'].strip())
                    year = row['year'].strip()
                    period = row['period'].strip()

                    # Add or update student record
                    student_id = self.add_record_from_import(
                        fname=row['fname'].strip(),
                        lname=row['lname'].strip(),
                        gender=row['gender'].strip(),
                        form=row['form'].strip(),
                        class_=row['class_'].strip(),
                        subject=row['subject'].strip(),
                        class_score=class_score,
                        exam_score=exam_score,
                        year=year,
                        period=period
                    )

                    if not student_id:
                        errors.append(f"Row {row_num}: Failed to insert/update student record")
                        continue

                    # Ensure academic record exists
                    self.get_or_create_student_identity(
                        fname=row['fname'].strip(),
                        lname=row['lname'].strip(),
                        gender=row['gender'].strip(),
                        form=row['form'].strip(),
                        class_=row['class_'].strip(),
                        year=year,
                        period=period
                    )

                    records_imported += 1


                    records_processed += 1

            # Show summary of the operation
            self.show_message(
                "Import Summary",
                f"Total Records Processed: {records_processed}\n"
                f"Records Imported: {records_imported}\n"
                f"Records Updated: {records_updated}\n"
                f"Errors: {len(errors)}",
                "info"
            )
            if errors:
                error_message = "\n".join(errors)
                self.show_message("Errors During Import", error_message, "error")


            # Refresh the display
        self.view_records()

    
     #===================================== export data to a CSV file ==========================================
    @db_error_handler
    def export_data(self):
        # Get selected class and subject from the Comboboxes
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        # Validate selected class
        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a valid class.","info")
            return

        # Base query
        query = """
                SELECT a.student_id, a.sch_code, a.student_num, a.index_num,
                        a.year, a.period, s.fname, s.lname, s.gender, s.form, s.class_,
                        s.subject, s.classScore, s.examScore, s.totalScore, s.grade
                FROM academic_records a
                JOIN students_records s ON s.id =  a.student_id
                WHERE  a.year = ? AND a.period = ? AND s.class_ = ?
                """
        parameters = [self.selected_year, self.selected_period, selected_class ]

        # Add subject filter if selected
        if selected_subject and selected_subject != "Choose Subject":
            query += " AND subject = ? ORDER BY totalScore DESC"
            parameters.append(selected_subject)

        # Fetch filtered data from the database
        records = self.run_query(query, parameters)

        # Ask the user where to save the file
        file_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return  # User canceled the save dialog

        # Write data to the CSV file
        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Student_id","School_code" ,"Student_num","Index_num","Year","Period",
                                "First_Name", "Last_Name", "Gender", "Form","Class", "Subject",
                                "Class_Score","Exams_Score", "Total_Score", "Grade & Remarks"])  # Header row
            for record in records:
                writer.writerow(record)

        self.show_message("Export Successful", f"Data exported successfully to {file_path}", "success")
        

   #========================================= Export to Import ===========================================
    @db_error_handler
    def export_csv_window(self):
        """Open a window to retrieve student data based on Class, Subject, Year, and Period."""
        export_win = Toplevel(self.root)
        export_win.title("Export Records")
        export_win.geometry("1000x500")
        export_win.configure(bg="#2E2E2E")
        self.center_window(export_win)
        export_win.grab_set()

        row_frame = Frame(export_win, bg="#2E2E2E")
        row_frame.grid(row=0, column=0, columnspan=6, pady=10)

        # --- Class ---
        class_frame = Frame(row_frame, bg="#2E2E2E")
        class_frame.pack(side=LEFT, padx=10)
        Label(class_frame, text="Class:", bg="#2E2E2E", fg="white").pack(side=LEFT)
        class_cb = ttk.Combobox(class_frame, width=12, state="readonly")
        class_cb.pack(side=LEFT)
    

        # --- Subject ---
        subject_frame = Frame(row_frame, bg="#2E2E2E")
        subject_frame.pack(side=LEFT, padx=10)
        Label(subject_frame, text="Subject:", bg="#2E2E2E", fg="white").pack(side=LEFT)
        subject_cb = ttk.Combobox(subject_frame, width=15, state="readonly")
        subject_cb.pack(side=LEFT)
    

        # Populate class and subject comboboxes base on user role
        self.populate_class_subject_comboboxes(class_cb, subject_cb)

         # --- Fetch Function ---
        
        def load_records():
            classes = class_cb.get()
            subjects = subject_cb.get()

            selected_class =classes
            selected_subject =subjects

            if  not selected_class or not selected_subject:
                self.show_message("Info", "Please select both Class and Subject.", "info")
                return

            query = """
                SELECT s.fname, s.lname, s.gender, s.form, s.class_, s.subject, s.classScore,
                        s.examScore, a.year, a.period FROM students_records s
                JOIN academic_records a ON a.id = s.student_id
                WHERE s.class_=? AND s.subject=?
            """
            rows = self.run_query(query, (selected_class, selected_subject)).fetchall() 

            # Clear existing item in Treeview
            for item in tree.get_children():
                tree.delete(item)
            #Insert new row
            for row in rows:
                tree.insert("", "end", values=row)

            if not rows:
                self.show_message("Info", "records found for the selected class and subject.", "info")
                return


        # --- Treeview ---
        cols = ("fname", "lname", "gender", "form", "class_", "subject", "classScore", "examScore", "year", "period")
        tree_frame = Frame(export_win)
        tree_frame.grid(row=2, column=0, columnspan=10, padx=5, pady=10, sticky="nsew")

        tree_scroll = Scrollbar(tree_frame)
        tree_scroll.pack(side=RIGHT, fill=Y)

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=80)

        tree.pack(fill=BOTH, expand=True)

        export_win.grid_rowconfigure(2, weight=1)
        export_win.grid_columnconfigure(0, weight=1)

       
        def export_to_csv():
            # Ask the user where to save the file
            file_path = asksaveasfilename(
                defaultextension=".csv", 
                filetypes=[("CSV files", "*.csv"), ("All files","*.*")],
                title="Save as"
            )
            if not file_path:
                return  # User canceled the save dialog
            # Write data to the CSV file
            with open(file_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(cols)  # Header row
                for item in tree.get_children():
                    row = tree.item(item)['values']
                    writer.writerow(row)
            self.show_message("Export Successful", f"Data exported successfully to {file_path}", "success")

        Button(export_win, text="Show Records", command=load_records, bg="blue", fg="white").grid(row=1, column=5, pady=10)
        Button(export_win, text="Export", command=export_to_csv, bg="green", fg="white").grid(row=1, column=6, pady=10)


   #========================================= selector function ==========================
    def create_selector_frame(self):
        """Create frame for class and subject selection"""
        # Create main frame
        frame = LabelFrame(
            self.root,
            bg='#1C1C1C',
            bd=2,
            relief=GROOVE,
            padx=10,
            pady=5
        )
        frame.grid(row=4, column=0, padx=10, pady=5, sticky=SW)

        # Title label
        Label(
            frame,
            text="Pick Data to Visualize",
            font=('inter', 11, 'bold'),
            fg='white',
            bg='navy',
        ).pack(fill=X)

        # Create sub-frames for better organization
        class_frame = Frame(frame, bg='#1C1C1C')
        class_frame.pack(fill=X, pady=5)
        
        subject_frame = Frame(frame, bg='#1C1C1C')
        subject_frame.pack(fill=BOTH, pady=0)

        # Class Selection
        Label(
            class_frame,
            text="Select Class:",
            font=("inter", 10),
            bg='#1C1C1C',
            fg="white",
            width=12,
            anchor=E
        ).pack(side=LEFT, padx=(10, 5))

        self.class_combobox = ttk.Combobox(
            class_frame,
            width=15,
            font=("inter", 10),
            state="readonly"
        )
        self.class_combobox.pack(side=LEFT, padx=(0,15))
        self.class_combobox.set("Choose Class")

        # Subject Selection
        Label(
            subject_frame,
            text="Select Subject:",
            font=("inter", 10),
            bg='#1C1C1C',
            fg="white",
            width=12,
            anchor=E
        ).pack(side=LEFT, padx=(10, 5))

        self.subject_combobox = ttk.Combobox(
            subject_frame,
            width=15,
            font=("inter", 10),
            state="readonly"
        )
        self.subject_combobox.pack(side=LEFT, padx=(0,15))
        self.subject_combobox.set("Choose Subject")

        # Populate class and subject comboboxes based on user role
        self.populate_class_subject_comboboxes(self.class_combobox, self.subject_combobox)

        # Bind events
        self.class_combobox.bind("<<ComboboxSelected>>", self.selector)
        self.subject_combobox.bind("<<ComboboxSelected>>", self.selector)

        # Style the comboboxes
        style = ttk.Style()
        style.configure(
            "TCombobox",
            fieldbackground="white",
            background="white",
            selectbackground="navy",
            selectforeground="white"
        )

        return frame

    
    # ============================= Fetch records ===================================
    def setup_main_filter_frame(self):
        """Creates the main filter frame on the app."""
        filter_frame = Frame(self.root, bg="#1C1C1C", bd=2, relief="groove")
        filter_frame.grid(row=4, column=1, padx=10, pady=10, sticky="se")

        Label(filter_frame, text="Filter by Year:", font= ("inter", 10), bg="#1C1C1C", fg="white").pack(side=LEFT, padx=(10, 5))
        self.year_entry = Entry(filter_frame, width=10)
        self.year_entry.insert(0, "2024/2025")
        self.year_entry.pack(side=LEFT, padx=(0, 15))
        
        periods_list =["Sem1", "Sem2", "Term1", "Term2", "Term3"]
        Label(filter_frame, text="Period:" ,font= ("inter", 10), bg="#1C1C1C", fg="white").pack(side=LEFT, padx=(10, 5))
        self.period_cb = ttk.Combobox(filter_frame, values=periods_list, width=10, state="readonly")
        self.period_cb.pack(side=LEFT, padx=(0,15))
        self.period_cb.set("Choose")
        

        Button(filter_frame, text="Show", font= ("inter", 10), bg="blue", fg="white", command=self.fetch_records).pack(side=LEFT, padx=5)
        read_button = Button(filter_frame, text="Read Aloud",bg="green",fg="white",command=self.read_treeview)
        read_button.pack(side=LEFT, padx=5)
        stop_button = Button(filter_frame, text="Stop",bg="red",fg="white", command=self.stop_reading)
        stop_button.pack(side=LEFT, padx=5)

    @clear_treeview
    def fetch_records(self):
        """Fetch and display student records based on year and period."""
        year = self.year_entry.get().strip()
        period = self.period_cb.get().strip()

        if not all([year, period]):
            self.show_message("Warning", "Year and Period are required.", "warning")
            return

        self.selected_year = year
        self.selected_period = period

        query = """
            SELECT s.fname, s.lname, s.gender, s.form, s.class_, s.subject,
                   s.classScore, s.examScore, s.totalScore, s.grade
            FROM academic_records a
            JOIN students_records s ON s.id = a.student_id
            WHERE a.year = ? AND a.period = ? ORDER BY s.lname
        """
        results = self.run_query(query, (year, period)).fetchall()

        for record in results:
            self.tree.insert("", "end", values=record)

        if not results:
            self.show_message("Info", "No records found for selected year and period.", "info")



   #========================================== Select Records ======================================================
    @clear_treeview
    @db_error_handler
    def selector(self, event=None):
        """Filter records based on the logged-in user? role and assignments"""
        # Get selected class and subject from the Comboboxes
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        if not hasattr(self, 'selected_year') or not hasattr(self, 'selected_period'):
            self.show_message("Warning", "Please select Year and Period first.", "info")
            return

        # Validate selected class
        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a valid class.", "info")
            return

        # Base query
        query = """
            SELECT a.student_id, s.fname, s.lname, s.gender, s.form, s.class_, s.subject,
                    s.classScore, s.examScore, s.totalScore, s.grade
            FROM academic_records a
            JOIN students_records s ON s.id = a.student_id
            WHERE a.year = ? AND a.period = ? AND s.class_ = ?
        """
        parameters = [self.selected_year, self.selected_period, selected_class]


        # Add subject filter if selected
        if selected_subject and selected_subject != "Choose Subject":
            query += " AND subject = ?"
            parameters.append(selected_subject)


        # Always add ORDER BY clause to sort by totalScore in descending order
        query += " ORDER BY totalScore DESC"

        # Execute the query
        records = self.run_query(query, parameters).fetchall()

        # Insert filtered records into the Treeview
        for record in records:
            self.tree.insert("", "end", text=record[0], values=record[1:])
            
        self.draw_hist() 
        self.draw_donut_plot()
        self.update_pass_percentage()
        self.grade_summary()


    #================================================ Plot Histogram ====================================
    @db_error_handler
    def draw_hist(self):
        # Get selected class and subject
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        # Validate selection
        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a valid class.", "info")
            return

        # Base query with proper SQL formatting
        query = """
            SELECT s.totalScore, COUNT(*) as frequency 
            FROM academic_records a
            JOIN students_records s ON s.id =  a.student_id
            WHERE  a.year = ? AND a.period = ? AND s.class_ = ? 
        """
        parameters = [self.selected_year, self.selected_period, selected_class]

        # Add subject filter
        if selected_subject and selected_subject != "Choose Subject":
            query += " AND subject = ?"
            parameters.append(selected_subject)

        query += " GROUP BY totalScore ORDER BY totalScore"

        # Execute query and fetch results
        result = self.run_query(query, parameters).fetchall()

        if not result:
            self.show_message("No Data", "No data available for plotting", "info")
            return

        # Create DataFrame directly from results
        scores = [row[0] for row in result]
        frequencies = [row[1] for row in result]
        df = pd.DataFrame({
            'Test Score': scores,
            'Frequency': frequencies
        })

        # Clear existing graph
        for widget in self.root.grid_slaves(row=0, column=2):
            widget.destroy()

        # Create frame for graph
        graph_frame = Frame(self.root, bg='white', bd=2, relief=RIDGE)
        graph_frame.grid(row=0, column=2, rowspan=5, padx=5, pady=5, sticky=NSEW)
        
        # Add title
        Label(graph_frame, 
            text=f" Academic Performance Analytics", 
            font=("inter", 12,"bold"), 
            fg="white",
            bg="navy",
            pady=5
            ).pack(fill=X)
        

        # Create histogram
        fig = plt.Figure(figsize=(5, 3.7), dpi=100)
        ax = fig.add_subplot(111)
        
        # Plot using seaborn
        seaborn.histplot(
            data=df,
            x='Test Score',
            weights='Frequency',
            bins=10,
            kde=True,
            ax=ax,
            alpha=0.75,
            linewidth=0.5,
            edgecolor='black',
            color='tab:green'
        )

        # Style the KDE line
        for line in ax.lines:
            line.set_color('darkred')  # Change KDE line color
            line.set_linestyle('-.')   # Make it dashed
            line.set_linewidth(1.5)    # Make it slightly thicker
        
        # Customize plot
        ax.set_title(
            f"{selected_class} - {selected_subject or ""}\nScore Distribution Analysis",
            fontsize=10,
            color="darkblue" 

            )
        ax.set_xlabel("Test Score")
        ax.set_ylabel("Frequency")

        # Embed plot
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH)

        # Adjust window size
        self.adjust_window_size()

        
    #============================================= Plot Donut ===================================================
    @db_error_handler
    def draw_donut_plot(self):
        """Create a donut plot showing pass/fail distribution"""
        # Get selected class and subject from the Comboboxes
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        # Validate selected class
        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a valid class.", "info")
            return

        # Base query for total students using PostgreSQL parameter style
        query_total = """
            SELECT COUNT(*) 
            FROM academic_records a
            JOIN students_records s ON s.id =  a.student_id
            WHERE  a.year = ? AND a.period = ? AND s.class_ = ? 
            """
        parameters = [self.selected_year, self.selected_period, selected_class]

        # Add subject filter if selected
        if selected_subject and selected_subject != "Choose Subject":
            query_total += " AND subject = ?"
            parameters.append(selected_subject)


        # Query for passed students
        query_pass = query_total + " AND totalScore >= 50"  # Assuming pass mark is 50

        total_students = self.run_query(query_total, parameters).fetchone()[0]
        passed_students = self.run_query(query_pass, parameters).fetchone()[0]


        # Check if there are any students
        if total_students == 0:
            self.show_message("No Data", "No data available for the selected class and subject!", "info")
            return

        # Calculate failed students
        failed_students = total_students - passed_students

        # Data for the donut plot
        labels = ['Passed Students', 'Failed Students']
        sizes = [passed_students, failed_students]
        colors = ['#31a354', '#f83232']  # Green for pass, red for fail

        # Create the donut plot
        fig = plt.Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            autopct='%1.1f%%',
            startangle=45,
            colors=colors,
            textprops=dict(color="black", fontsize=10),
            pctdistance= 1.23,
        )
        ax.set_title(
            f"Class Performance Overview: {selected_class} - {selected_subject}",
            fontsize =(10),
            pad=8, 
            color="darkblue"                        
        )
        
        legend = ax.legend(
            labels, 
            loc = 'center left', 
            fontsize = 8,
            frameon=True,
            bbox_to_anchor=(0.85, 0.85),
            edgecolor='darkgray'
            )

        # Add a hole in the center
        center_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(center_circle)

        # Clear existing plot
        for widget in self.root.grid_slaves(row=5, column=2):
            widget.destroy()

        # Create frame for the plot
        donut_frame = Frame(self.root, bg="white", bd=2, relief=RIDGE)
        donut_frame.grid(row=5, column=2, rowspan=5, padx=5, sticky=NSEW)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(5, weight=1)

        # Embed plot in frame
        canvas = FigureCanvasTkAgg(fig, master=donut_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=5, column=0)

        self.adjust_window_size()


    def adjust_window_size(self):
        """Adjust window size to fit all components including graphs"""
        # Wait for all widgets to be updated
        self.root.update_idletasks()
        
        # Calculate required width and height
        required_width = 1200  # Base width
        if self.root.grid_slaves(column=2):  # If graphs are present
            required_width = 1600  # Width including graphs
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Ensure window doesn't exceed screen size
        window_width = min(required_width, screen_width * 0.9)
        window_height = min(800, screen_height * 0.9)
        
        # Calculate center position
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # Set new window size and position
        self.root.geometry(f"{int(window_width)}x{int(window_height)}+{center_x}+{center_y}")

    
    #=================================== Percentage passed function ===========================
    @db_error_handler
    def update_pass_percentage(self):
        """Calculate and display pass/fail percentage with arrow bars"""
        # Get selected class and subject
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        if not selected_class or selected_class == "Choose Class":
            self.percentage_label.config(text="0%")
            self.show_message("Info", "Please select a valid class.", "info")
            return

        # Base query for total students
        query_total = """
            SELECT COUNT(*) 
            FROM academic_records a
            JOIN students_records s ON s.id =  a.student_id
            WHERE  a.year = ? AND a.period = ? AND s.class_ = ?
        """
        parameters = [self.selected_year, self.selected_period, selected_class]

        if selected_subject and selected_subject != "Choose Subject":
            query_total += " AND subject = ?"
            parameters.append(selected_subject)

        # Query for passed students
        query_pass = query_total + " AND totalScore >= 50"

        # Execute queries
        total_students = self.run_query(query_total, parameters).fetchone()[0]
        passed_students = self.run_query(query_pass, parameters).fetchone()[0]
        failed_students = total_students - passed_students

        # Calculate percentages
        if total_students > 0:
            pass_percentage = (passed_students / total_students) * 100
            fail_percentage = (failed_students / total_students) * 100
        else:
            pass_percentage = fail_percentage = 0

        # Clear existing widgets
        for widget in self.root.grid_slaves(row=0, column=1):
            widget.destroy()

        # Create frame for percentage display
        percentage_frame = Frame(self.root, bg='white', bd=2, relief=RIDGE)
        percentage_frame.grid(row=0, column=1, padx=0, pady=20, sticky=NW)

        # Title
        Label(percentage_frame,
            text=f"{selected_class} Performance Overview",
            font=("inter", 11, "bold"),
            bg='navy',
            fg='white',
            pady=5,
            width=20
        ).pack(fill=X)

        # Pass percentage arrow bar
        pass_frame = Frame(percentage_frame, bg='white', pady=5)
        pass_frame.pack(fill=X, padx=10)
        Label(pass_frame,
            text="Pass:",
            font=("inter", 10),
            bg='white',
            width=8,
            anchor=W
        ).pack(side=LEFT)
        
        # Create canvas for pass arrow
        pass_canvas = Canvas(pass_frame, height=20, width=150, bg='white', bd=0, highlightthickness=0)
        pass_canvas.pack(side=LEFT, padx=5)
        
        # Draw pass arrow
        arrow_width = (pass_percentage / 100) * 150
        pass_canvas.create_rectangle(0, 5, arrow_width, 15, fill='green', width=0)
        pass_canvas.create_polygon(
            arrow_width, 0,
            arrow_width, 20,
            arrow_width + 10, 10,
            fill='green'
        )
        Label(pass_frame,
            text=f"{pass_percentage:.1f}%",
            font=("inter", 10),
            bg='white'
        ).pack(side=LEFT)

        # Fail percentage arrow bar
        fail_frame = Frame(percentage_frame, bg='white', pady=5)
        fail_frame.pack(fill=X, padx=10)
        Label(fail_frame,
            text="Fail:",
            font=("inter", 10),
            bg='white',
            width=8,
            anchor=W
        ).pack(side=LEFT)
        
        # Create canvas for fail arrow
        fail_canvas = Canvas(fail_frame, height=20, width=150, bg='white', bd=0, highlightthickness=0)
        fail_canvas.pack(side=LEFT, padx=5)
        
        # Draw fail arrow
        arrow_width = (fail_percentage / 100) * 150
        fail_canvas.create_rectangle(0, 5, arrow_width, 15, fill='red', width=0)
        fail_canvas.create_polygon(
            arrow_width, 0,
            arrow_width, 20,
            arrow_width + 10, 10,
            fill='red'
        )
        Label(fail_frame,
            text=f"{fail_percentage:.1f}%",
            font=("inter", 10),
            bg='white'
        ).pack(side=LEFT)

        # Add total students count
        Label(percentage_frame,
            text=f"Total Students: {total_students}",
            font=("inter", 10),
            bg='white',
            pady=5
        ).pack()


   #=======================Grade Summary =======================
    @db_error_handler
    def grade_summary(self):
        """Create and display number of students per grade for selected class and subject."""
        # Get selected class and subject
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a valid class.", "info")
            return

        # Build and execute query
        query = """
            SELECT s.grade 
            FROM academic_records a
            JOIN students_records s ON s.id =  a.student_id
            WHERE  a.year = ? AND a.period = ? AND s.class_ = ?
            """
        parameters = [self.selected_year, self.selected_period, selected_class]

        if selected_subject and selected_subject != "Choose Subject":
            query += " AND subject = ?"
            parameters.append(selected_subject)

        query += " ORDER BY totalScore DESC"
        records = self.run_query(query, parameters)

        
        # Destroy old frame if it exists (to refresh content)
        if hasattr(self, 'grade_frame') and self.grade_frame.winfo_exists():
            self.grade_frame.destroy()

        # Create frame
        self.grade_frame = LabelFrame(
            self.root,
            bg='white',
            padx=10,
            relief=RIDGE
        )
        self.grade_frame.grid(row=0, column=1, sticky=E, padx=10, pady=20)

        grade_label = Label(
            self.grade_frame,
            text="Grade Summary", 
            font=('inter', 11, 'bold'), 
            fg="white", bg="navy"
        )
            
        grade_label.pack(fill=BOTH)

        # Count grades and display
        self.grade_labels = {}
        grade_counts = Counter(record[0] for record in records)  # grade at index 10

        grades = [
                    "A1  Excellent", "B2  Very Good", "B3  Good", "C4  Credit",
                    "C5  Credit", "C6  Credit", "D7  Pass", "E8  Pass", "F9  Fail"
                ]


        for grade in grades:
            count = grade_counts.get(grade, 0)

            label = Label(
                self.grade_frame,
                text=f"{grade}: {count}",
                font=('inter', 10),
                bg='white',
                anchor='w'
            )
            label.pack(fill=X, pady=1)

            self.grade_labels[grade] = label

                # Add a red separator line **after D7**
            if grade == "C6  Credit":
                # Create a canvas wide enough for the full width of the frame
                line_canvas = Canvas(self.grade_frame, height=2, width=100, bg='white', highlightthickness=0)
                line_canvas.pack(fill=X, pady=5)

                # Draw a horizontal red line across the canvas
                line_canvas.create_line(0, 2, 100, 2, fill='red', width=2)


  #=============================== Class Stats ============================
    @db_error_handler
    def show_class_stats(self):
        """Show descriptive statistics for the selected class"""
        # Get selected class and subject
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        # Validate selection
        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a class first.", "info")
            return

        # Create stats window
        stats_window = Toplevel(self.root)
        stats_window.title(f"Class Statistics - {selected_class}")
        stats_window.geometry("800x600")
        stats_window.config(bg="lavender")
        stats_window.grab_set()

        # Center the window
        self.center_window(stats_window)

        # Fetch data from database
        query = """
            SELECT classScore, examScore, totalScore, gender 
            FROM academic_records a
            JOIN students_records s ON s.id =  a.student_id
            WHERE  a.year = ? AND a.period = ? AND s.class_ = ?
        """
        params = [self.selected_year, self.selected_period, selected_class]

        if selected_subject and selected_subject != "Choose Subject":
            query += " AND subject = ?"
            params.append(selected_subject)

        result = self.run_query(query, params).fetchall()
        
        if not result:
            self.show_message("Error", "No data available for selected criteria.", "error")
            stats_window.destroy()
            return

        # Convert to pandas DataFrame
        df = pd.DataFrame(result, columns=['Class Score', 'Exam Score', 'Total Score', 'Gender'])

        # Calculate descriptive statistics
        stats_frame = Frame(stats_window, bg="lavender", bd=2, relief=RIDGE)
        stats_frame.pack(fill=X, padx=10, pady=10)

        stats_label = Label(
            stats_frame,
            text="Descriptive Statistics",
            font=("inter", 12, "bold"),
            bg="navy",
            fg="white",
            pady=5
        )
        stats_label.pack(fill=X)

        # Create statistics table
        stats_text = Text(stats_frame, height=8, width=80, font=("Courier", 10))
        stats_text.pack(padx=10, pady=5)

        # Calculate and display statistics
        for column in ['Class Score', 'Exam Score', 'Total Score']:
            stats = df[column].describe()
            stats_text.insert(END, f"\n{column:^30}\n")
            stats_text.insert(END, "-" * 30 + "\n")
            stats_text.insert(END, f"Mean     : {stats['mean']:>8.2f}\n")
            stats_text.insert(END, f"Std Dev  : {stats['std']:>8.2f}\n")
            stats_text.insert(END, f"Minimum  : {stats['min']:>8.2f}\n")
            stats_text.insert(END, f"Maximum  : {stats['max']:>8.2f}\n")
            stats_text.insert(END, "\n")

        stats_text.config(state=DISABLED)

        # Create gender comparison graph
        graph_frame = Frame(stats_window, bg="lavender", bd=2, relief=RIDGE)
        graph_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        # Calculate mean scores by gender
        gender_stats = df.groupby('Gender')[['Class Score', 'Exam Score', 'Total Score']].mean()

        # Create bar plot
        bar_width = 0.25
        index = np.arange(len(gender_stats.columns))

        for i, gender in enumerate(gender_stats.index):
            ax.bar(
                index + i * bar_width,
                gender_stats.loc[gender],
                bar_width,
                label=gender,
                color='#0066CC' if gender == 'M' else '#92C5F9'
            )

        # Customize plot
        ax.set_ylabel('Mean Score')
        ax.set_title(f'Performance by Gender - {selected_class} {selected_subject or ""}')
        ax.set_xticks(index + bar_width / 2)
        ax.set_xticklabels(['Class Score', 'Exam Score', 'Total Score'])
        ax.legend()

        # Embed plot
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)


    # ======================================== print data ==================================================
    @db_error_handler
    def print_data(self):
        """Print records with preview option"""
        # Get selected class and subject
        selected_class = self.class_combobox.get()
        selected_subject = self.subject_combobox.get()

        if not selected_class or selected_class == "Choose Class":
            self.show_message("Info", "Please select a valid class.", "info")
            return

        # Create preview window
        preview_window = Toplevel(self.root)
        preview_window.title("Print Preview")
        preview_window.geometry("1000x600")
        preview_window.config(bg="white")
        preview_window.grab_set()
    

        # Create preview frame
        preview_frame = Frame(preview_window, bg="white", padx=20, pady=20)
        preview_frame.pack(fill=BOTH, expand=True)

        # Add scrollbar
        canvas = Canvas(preview_frame, bg="white")
        scrollbar = ttk.Scrollbar(preview_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Header
        Label(scrollable_frame, 
            text="JUABOSO SENIOR HIGH SCHOOL (JUASEC)", 
            font=('inter', 16, 'bold'), 
            bg="white").grid(row=0, column=0, columnspan=8, pady=10)

        Label(scrollable_frame, 
            text=f"Class: {selected_class}   Subject: {selected_subject}   Year: {self.selected_year}  Period: {self.selected_period}", 
            font=('inter', 12, 'bold'), 
            bg="white").grid(row=1, column=0, columnspan=8, pady=5)

        # Column headers
        headers = ["ID", "First Name", "Last Name", "Class Score", "Exam Score", "Total Score", "Grade"]
        for col, header in enumerate(headers):
            Label(scrollable_frame, 
                text=header, 
                font=('inter', 10, 'bold'), 
                bg="white",
                borderwidth=1,
                relief="solid",
                width=15,
                padx=5).grid(row=2, column=col, pady=5)

        # Get data
        query = """
                SELECT a.student_num, s.fname, s.lname, s.classScore, s.examScore, s.totalScore, s.grade 
                FROM students_records s
                JOIN academic_records a ON s.id = a.student_id
                WHERE  a.year = ? AND a.period = ? AND s.class_ = ?
            """
        params = [self.selected_year, self.selected_period, selected_class]

        if selected_subject and selected_subject != "Choose Subject":
            query += " AND subject = ?"
            params.append(selected_subject)

        query += " ORDER BY totalScore DESC"
        records = self.run_query(query, params).fetchall()

        # Display data
        for row_idx, record in enumerate(records, start=3):
            for col_idx, value in enumerate(record):
                Label(scrollable_frame, 
                    text=str(value),
                    font=('inter', 10),
                    bg="white",
                    borderwidth=1,
                    relief="solid",
                    width=15,
                    padx=5).grid(row=row_idx, column=col_idx, pady=1)

        # Layout for scrollable preview
        canvas.grid(row=0, column=0, sticky=NSEW)
        scrollbar.grid(row=0, column=1, sticky=NS)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_rowconfigure(0, weight=1)

        # Buttons frame
        button_frame = Frame(preview_window, bg="white", pady=10)
        button_frame.pack(fill=X)

        # Print button
        Button(button_frame,
            text="Print",
            command=lambda: self.print_to_printer(records, selected_class, selected_subject),
            bg="green",
            fg="white",
            font=("inter", 10, "bold"),
            padx=20).pack(side=LEFT, padx=5)

        # Save as PDF button
        Button(button_frame,
            text="Save as PDF",
            command=lambda: self.save_as_pdf(records, selected_class, selected_subject),
            bg="blue",
            fg="white",
            font=("inter", 10, "bold"),
            padx=20).pack(side=LEFT, padx=5)

        # Cancel button
        Button(button_frame,
            text="Cancel",
            command=preview_window.destroy,
            bg="red",
            fg="white",
            font=("inter", 10, "bold"),
            padx=20).pack(side=LEFT, padx=5)


    @db_error_handler
    def print_to_printer(self, records, selected_class, selected_subject):
        """Send the records to selected printer"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp:
            temp_file_path = temp.name
            temp.write("JUABOSO SENIOR HIGH SCHOOL (JUASEC)\n")
            temp.write("=" * 80 + "\n")
            temp.write(f"Class: {selected_class}   Subject: {selected_subject}   Year: {self.selected_year}  Period: {self.selected_period}\n")
            temp.write("=" * 80 + "\n\n")
            temp.write(f"{'ID':<5}{'First Name':<15}{'Last Name':<15}"
                    f"{'Class Score':<12}{'Exam Score':<12}{'Total Score':<12}{'Grade':<15}\n")

            for record in records:
                temp.write(f"{str(record[0]):<5}{record[1]:<15}{record[2]:<15}"
                        f"{str(record[3]):<12}{str(record[4]):<12}{str(record[5]):<12}{record[6]:<15}\n")

        # Prompt printer selection
        printer_name = win32print.GetDefaultPrinter()
        printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        
        selected = simpledialog.askstring("Select Printer", f"Available printers:\n\n" +
                                        "\n".join(printers) + "\n\nEnter printer name:",
                                        initialvalue=printer_name)
        if not selected or selected not in printers:
            self.show_message("Cancelled", "Printing cancelled or invalid printer name.", "warning")
            return

        # Send to selected printer
        win32api.ShellExecute(
            0,
            "printto",
            temp_file_path,
            f'"{selected}"',
            ".",
            0
        )

    @db_error_handler
    def save_as_pdf(self, records, selected_class, selected_subject):
        """Save the records as PDF"""
            # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )

        if not file_path:
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "JUABOSO SENIOR HIGH SCHOOL (JUASEC)", ln=True, align="C")
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Class: {selected_class}   Subject: {selected_subject}   Year: {self.selected_year}  Period: {self.selected_period}", ln=True, align="C")
        pdf.ln(5)

        # Table headers
        pdf.set_font("helvetica", "B", 10)
        headers = ["ID", "First Name", "Last Name", "Class Score", "Exam Score", "Total Score", "Grade"]
        col_widths = [15, 30, 30, 25, 25, 25, 30]
        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 8, header, border=1, align="C")
        pdf.ln()

        # Table data
        pdf.set_font("helvetica", "", 10)
        for record in records:
            for i, value in enumerate(record):
                pdf.cell(col_widths[i], 8, str(value), border=1, align="C")
            pdf.ln()

        pdf.output(file_path)
        self.show_message("Success", f"File saved as: {file_path}", "success")


  #======================== Print Report =========================
    @db_error_handler
    def print_report(self):
        def generate_report():
            # Get student details
            selected_firstname = firstname_var.get().strip()
            selected_lastname = lastname_var.get().strip()
            selected_class = self.class_combobox.get()
            selected_subject = self.subject_combobox.get()

            # Validate inputs
            if not selected_firstname or not selected_lastname:
                self.show_message("Info", "Please enter both first and last name.", "info")
                return
            if not selected_class or selected_class == "Choose Class":
                self.show_message("Info", "Please select a valid class.", "info")
                return

            # Single query to fetch records with position calculation
            query = """
                SELECT 
                    t1.fname,
                    t1.lname,
                    t1.subject,
                    t1.totalScore,
                    t1.grade,
                    (
                        SELECT COUNT(*) + 1 
                        FROM students_records t2 
                        WHERE t2.class_ = t1.class_ 
                        AND t2.subject = t1.subject 
                        AND t2.totalScore > t1.totalScore
                    ) as position
                FROM students_records t1
                WHERE UPPER(t1.fname) = UPPER(?) 
                AND UPPER(t1.lname) = UPPER(?) 
                AND t1.class_ = ?
            """
            parameters = [selected_firstname, selected_lastname, selected_class]

            # Add subject filter if selected
            if selected_subject and selected_subject != "Choose Subject":
                query += " AND t1.subject = ?"
                parameters.append(selected_subject)

            # Order by subject
            query += " ORDER BY t1.subject"

            # Execute query
            records = self.run_query(query, parameters).fetchall()

            if not records:
                self.show_message("Error", "No records found for this student.", "error")
                return

            # Continue with displaying the report...

            # Create preview window
            preview_window = Toplevel(self.root)
            preview_window.title("Report Preview")
            preview_window.geometry("900x600")
            preview_window.config(bg="white")
            preview_window.grab_set()


            # Add scrollbar and canvas
            canvas = Canvas(preview_window, bg="white")
            scrollbar = ttk.Scrollbar(preview_window, orient=VERTICAL, command=canvas.yview)
            scrollable_frame = Frame(canvas, bg="white")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
            canvas.configure(yscrollcommand=scrollbar.set)

            # Header
            Label(scrollable_frame, 
                text="JUABOSO SENIOR HIGH SCHOOL (JUASEC)",
                font=('inter', 16, 'bold'),
                bg="white").grid(row=0, column=0, columnspan=3, pady=10)

            Label(scrollable_frame,
                text="STUDENT'S ACADEMIC PERFORMANCE",
                font=('inter', 14, 'bold'),
                bg="white").grid(row=1, column=0, columnspan=3, pady=5)

            # Student details
            details_frame = Frame(scrollable_frame, bg="white", relief=RIDGE, bd=2)
            details_frame.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky=EW)

            Label(details_frame, text=f"Student Name: {selected_firstname} {selected_lastname}",
                font=('inter', 12), bg="white").grid(row=0, column=0, padx=10, pady=5, sticky=W)
            Label(details_frame, text=f"Class: {selected_class}",
                font=('inter', 12), bg="white").grid(row=1, column=0, padx=10, pady=5, sticky=W)

            # Column headers
            headers = ["Subject", "Total Score", "Grade & Remarks", "Position"]
            for col, header in enumerate(headers):
                Label(scrollable_frame, text=header,
                    font=('inter', 11, 'bold'),
                    bg="white",
                    relief=RIDGE,
                    width=15,
                    anchor=CENTER  # Center the header text
                ).grid(row=3, column=col, padx=2, pady=5)

            # The data rows
            for row_idx, record in enumerate(records, start=4):
                # Subject
                Label(scrollable_frame, text=record[2],
                    font=('inter', 10),
                    bg="white",
                    relief=RIDGE,
                    width=20,
                ).grid(row=row_idx, column=0, padx=2, pady=2)
                
                # Total Score
                Label(scrollable_frame, text=str(record[3]),
                    font=('inter', 10),
                    bg="white",
                    relief=RIDGE,
                    width=20,
                    anchor=CENTER  # Center the text
                ).grid(row=row_idx, column=1, padx=2, pady=2)
                
                # Grade & Remarks
                Label(scrollable_frame, text=record[4],
                    font=('inter', 10),
                    bg="white",
                    relief=RIDGE,
                    width=20,
                    anchor=CENTER  # Center the text
                ).grid(row=row_idx, column=2, padx=2, pady=2)
                
                # Position with suffix
                position = record[-1]
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(
                    position if position < 20 else position % 10, 
                    'th'
                )
                position_text = f"{position}{suffix}"
                
                Label(scrollable_frame, 
                    text=position_text,
                    font=('inter', 10, 'bold') if position <= 3 else ('inter', 10),
                    fg='darkgreen' if position <= 3 else 'black',
                    bg="white",
                    relief=RIDGE,
                    width=20,
                    anchor=CENTER  # Center the text
                ).grid(row=row_idx, column=3, padx=2, pady=2)
            
            # Add footer with editable remarks
            footer_frame = Frame(scrollable_frame, bg="white", relief=RIDGE, bd=2)
            footer_frame.grid(row=row_idx+1, column=0, columnspan=3, padx=20, pady=20, sticky=EW)

            # Add remarks text area
            Label(footer_frame, text="Form Master's Remarks:", 
                font=('inter', 10, 'bold'), bg="white").grid(row=0, column=0, padx=10, pady=5, sticky=W)
            remarks_text = Text(footer_frame, height=3, width=50, font=('inter', 10))
            remarks_text.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky=EW)

            # Add placeholder text
            remarks_placeholder = "Enter remarks here (max 200 characters)..."
            remarks_text.insert('1.0', remarks_placeholder)
            remarks_text.config(fg='gray')

            # Add events to handle placeholder text
            def on_focus_in(event):
                if remarks_text.get('1.0', 'end-1c') == remarks_placeholder:
                    remarks_text.delete('1.0', END)
                    remarks_text.config(fg='black')

            def on_focus_out(event):
                if not remarks_text.get('1.0', 'end-1c'):
                    remarks_text.insert('1.0', remarks_placeholder)
                    remarks_text.config(fg='gray')

            remarks_text.bind('<FocusIn>', on_focus_in)
            remarks_text.bind('<FocusOut>', on_focus_out)

            # Limit text to 200 characters
            def limit_chars(*args):
                if len(remarks_text.get('1.0', END)) > 201:  # 201 accounts for newline char
                    remarks_text.delete('200.0', END)

            remarks_text.bind('<KeyPress>', limit_chars)

            # Other footer elements
            Label(footer_frame, text="Form Master Name:", 
                font=('inter', 10), bg="white").grid(row=2, column=0, padx=10, pady=5, sticky=W)
            name_entry = Entry(footer_frame, width=30, font=('inter', 10))
            name_entry.grid(row=2, column=1, padx=10, pady=5, sticky=W)

            Label(footer_frame, text="Date:", 
                font=('inter', 10), bg="white").grid(row=3, column=0, padx=10, pady=5, sticky=W)
            date_entry = Entry(footer_frame, width=30, font=('inter', 10))
            date_entry.grid(row=3, column=1, padx=10, pady=5, sticky=W)
            # Insert current date
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            date_entry.insert(0, current_date)

            Label(footer_frame, text="Signature:", 
                font=('inter', 10), bg="white").grid(row=4, column=0, padx=10, pady=5, sticky=W)
            signature_entry = Entry(footer_frame, width=30, font=('inter', 10))
            signature_entry.grid(row=4, column=1, padx=10, pady=5, sticky=W)


                # Headmaster section / footer elements
            Label(footer_frame, text="Headmaster Name:", 
                font=('inter', 10), bg="white").grid(row=5, column=0, padx=10, pady=5, sticky=W)
            name_entry = Entry(footer_frame, width=30, font=('inter', 10))
            name_entry.grid(row=5, column=1, padx=10, pady=5, sticky=W)

            Label(footer_frame, text="Date:", 
                font=('inter', 10), bg="white").grid(row=6, column=0, padx=10, pady=5, sticky=W)
            date_entry = Entry(footer_frame, width=30, font=('inter', 10))
            date_entry.grid(row=6, column=1, padx=10, pady=5, sticky=W)
            # Insert current date
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            date_entry.insert(0, current_date)

            Label(footer_frame, text="Signature:", 
                font=('inter', 10), bg="white").grid(row=7, column=0, padx=10, pady=5, sticky=W)
            signature_entry = Entry(footer_frame, width=30, font=('inter', 10))
            signature_entry.grid(row=7, column=1, padx=10, pady=5, sticky=W)

            # Layout scrollbar and canvas
            canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=10, pady=10)
            scrollbar.pack(side=RIGHT, fill=Y)

            # Buttons frame
            button_frame = Frame(preview_window, bg="white")
            button_frame.pack(fill=X, pady=10)

            Button(button_frame,
                text="Print",
                command=lambda: self.print_report_to_printer(records, selected_firstname, 
                    selected_lastname, selected_class),
                bg="green",
                fg="white",
                font=("inter", 10, "bold")).pack(side=LEFT, padx=5)

            Button(button_frame,
                text="Save as PDF",
                command=lambda: self.save_report_as_pdf(records, selected_firstname, 
                    selected_lastname, selected_class),
                bg="blue",
                fg="white",
                font=("inter", 10, "bold")).pack(side=LEFT, padx=5)

            Button(button_frame,
                text="Close",
                command=preview_window.destroy,
                bg="red",
                fg="white",
                font=("inter", 10, "bold")).pack(side=LEFT, padx=5)


        # Create input window
        report_window = Toplevel(self.root)
        report_window.title("Student Report")
        report_window.geometry("400x200")
        report_window.config(bg="lavender")
        report_window.grab_set()


        # Input fields
        firstname_var = StringVar()
        lastname_var = StringVar()

        Label(report_window, text="Enter First Name:", font=("inter", 12), bg="lavender").grid(
            row=0, column=0, padx=10, pady=10, sticky=W)
        Entry(report_window, width=30, textvariable=firstname_var).grid(
            row=0, column=1, padx=10, pady=10)

        Label(report_window, text="Enter Last Name:", font=("inter", 12), bg="lavender").grid(
            row=1, column=0, padx=10, pady=10, sticky=W)
        Entry(report_window, width=30, textvariable=lastname_var).grid(
            row=1, column=1, padx=10, pady=10)

        Button(report_window,
            text="Generate Preview",
            command=generate_report,
            bg="green",
            fg="white",
            font=("inter", 10, "bold")).grid(row=2, column=1, pady=20, sticky=E)
        
    @db_error_handler    
    def print_report_to_printer(self, records, firstname, lastname, selected_class):
        """Print student report to printer"""
        # Create a temporary file for printing
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as file:
            temp_file_path = file.name
            # Write header
            file.write("\n")
            file.write("JUABOSO SENIOR HIGH SCHOOL (JUASEC)\n")
            file.write("=" * 80 + "\n")
            file.write("STUDENT'S ACADEMIC PERFORMANCE REPORT\n")
            file.write("=" * 80 + "\n\n")

            # Write student details
            file.write(f"Student Name: {firstname} {lastname}\n")
            file.write(f"Class: {selected_class}\n")
            file.write("-" * 80 + "\n\n")

            # Write column headers
            file.write(f"{'Subject':<30}{'Total Score':<15}{'Grade & Remarks':<20}{'Position':<20}\n")
            file.write("-" * 80 + "\n")

            # Write subject records
            for record in records:
                file.write(f"{record[2]:<30}{str(record[3]):<15}{record[4]:<20}{record[5]:<20}\n")

            file.write("\n" + "=" * 80 + "\n\n")

            # Add footer for signatures
            file.write("Form Master's Remarks: .............................\n")
            file.write("Form Master Name: .............................\n")
            file.write("Date: .............................\n")
            file.write("Signature: .............................\n")

            file.write("\n")

            #Headmaster Signature
            # Add footer for signatures
            file.write("Headmaster Name: .............................\n")
            file.write("Date: .............................\n")
            file.write("Signature: .............................\n")


    # Prompt printer selection
        printer_name = win32print.GetDefaultPrinter()
        printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        
        selected = simpledialog.askstring("Select Printer", f"Available printers:\n\n" +
                                        "\n".join(printers) + "\n\nEnter printer name:",
                                        initialvalue=printer_name)
        if not selected or selected not in printers:
            self.show_message("Cancelled", "Printing cancelled or invalid printer name.", "warning")
            return

        # Send to selected printer
        win32api.ShellExecute(
            0,
            "printto",
            temp_file_path,
            f'"{selected}"',
            ".",
            0
        )

    @db_error_handler
    def save_report_as_pdf(self, records, firstname, lastname, selected_class):
        """Save student report as PDF"""
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report As PDF"
        )

        if not file_path:
            return

        # Create PDF document
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Header
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "JUABOSO SENIOR HIGH SCHOOL (JUASEC)", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, "STUDENT'S ACADEMIC PERFORMANCE REPORT", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)

        # Student details
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"Student Name: {firstname} {lastname}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 10, f"Class: {selected_class}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)

        # Table headers
        pdf.set_font("helvetica", "B", 11)
        pdf.cell(50, 6, "Subject", border=1)
        pdf.cell(40, 6, "Total Score", border=1)
        pdf.cell(50, 6, "Grade & Remarks", border=1)
        pdf.cell(30, 6, "Position", border=1, ln=True)

        # Table data
        pdf.set_font("helvetica", "", 11)
        for record in records:
            pdf.cell(50, 6, str(record[2]), border=1)
            pdf.cell(40, 6, str(record[3]), border=1)
            pdf.cell(50, 6, str(record[4]), border=1)
            pdf.cell(30, 6, str(record[5]), border=1, ln=True)
                    
        # Footer
        pdf.ln(20)
        pdf.set_font("helvetica", "", 11)
        
        # Update all footer cells with new positioning parameters
        footer_items = [
            "Form Master's Remarks: .............................",
            "Form Master Name: .............................",
            "Date: .............................",
            "Signature: .............................",
            " ",  # Spacing
            "Headmaster Name: .............................",
            "Date: .............................",
            "Signature: ............................."
        ]

        for item in footer_items:
            pdf.cell(0, 10, item, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Save PDF
        pdf.output(file_path)
        self.show_message("Success", f"Report saved as: {file_path}", "success")
    

    #=============================== Convert report PDF to Word Docx ====================================
    @db_error_handler
    def convert_pdf_docx(self):
        try:
            # File dialog to select PDF file
            file_path = filedialog.askopenfilename(
                title="Select PDF File to Import",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
            )

            if not file_path:
                return

            # Create the output .docx path
            docx_path = os.path.splitext(file_path)[0] + ".docx"

            # Convert PDF to DOCX
            cv = Converter(file_path)
            cv.convert(docx_path, start=0 , end=None)
            cv.close()

            self.show_message("Success", f"Conversion complete: {docx_path}", "success")

        except Exception as e:
            self.show_message("Error", f"PDF to Docx conversion error: {e}", "error")

    #================================= PDF Merger ====================================
    @db_error_handler
    def merge_pdfs(self):
        # Select multiple PDF files
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files to Merge",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if not file_paths:
            return

        # Ask where to save the merged PDF
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title="Save Merged PDF As"
        )
        if not output_path:
            return

        merger = PdfWriter()
        for path in file_paths:
            merger.append(path)
        merger.write(output_path)
        merger.close()
        self.show_message("Success", "PDF files merged successfully!", "success")

    #=================================== Read text ======================================
    @db_error_handler
    def read_treeview(self):
        # Make sure Treeview exists
        if not hasattr(self, 'tree'):
            print("Treeview not initialized.")
            return

        # Initialize speech engine
        speak = pyttsx3.init()

        # Iterate over all rows in the Treeview
        for row_id in self.tree.get_children():
            row_values = self.tree.item(row_id, "values")
            if row_values:
                # Convert tuple to string and speak
                text = " | ".join(str(value) for value in row_values)
                self.engine.say(text)
        self.engine.runAndWait()

    def stop_reading(self):
        self.engine.stop()

       #================================== Add Calculator ================================
    def calculator(self):
        def num(value):
            """Append the pressed button? value to the operator."""
            nonlocal operator
            operator += str(value)
            txt_input.set(operator)

        def clear():
            """Clear the input field and reset the operator."""
            nonlocal operator
            operator = ""
            txt_input.set("")
        
        def equal():
            """Evaluate the expression and display the result."""
            nonlocal operator
            try:
                # Safely evaluate the expression
                result = eval(operator)
                txt_input.set(result)
                operator = str(result)  # Allow further calculations
            except Exception:
                txt_input.set("Error")
                operator = ""

        # Create a new window for the calculator
        cal_window = Toplevel(self.root)
        cal_window.title("Calculator")
        cal_window.config(bg="alice blue")
        cal_window.resizable(False, False)  # Prevent resizing of the calculator window
        cal_window.grab_set()


        # Initialize the operator and input field
        operator = ""
        txt_input = StringVar(value="")

        # ======================= Screen ===========================
        display = Entry(
            cal_window,
            font=('inter', 25, 'bold'),
            fg='white',
            bg="steel blue",
            justify='right',
            bd=30,
            textvariable=txt_input,
        )
        display.grid(columnspan=4)

        # ======================= Buttons ==========================
        button_config = {
            "font": ('inter', 14, 'bold'),
            "bd": 8,
            "pady": 15,
        }

        # Row 1
        Button(cal_window, text="C", bg='orange red', padx=34, command=clear, **button_config).grid(row=1, column=0)
        Button(cal_window, text="(", bg='darkgreen', padx=38, command=lambda: num("("), **button_config).grid(row=1, column=1)
        Button(cal_window, text=")", bg='darkgreen', padx=38, command=lambda: num(")"), **button_config).grid(row=1, column=2)
        Button(cal_window, text="%", bg='darkgreen', padx=37, command=lambda: num("/"), **button_config).grid(row=1, column=3)

        # Row 2
        Button(cal_window, text="7", bg='lightcyan', padx=34, command=lambda: num(7), **button_config).grid(row=2, column=0)
        Button(cal_window, text="8", bg='lightcyan', padx=34, command=lambda: num(8), **button_config).grid(row=2, column=1)
        Button(cal_window, text="9", bg='lightcyan', padx=34, command=lambda: num(9), **button_config).grid(row=2, column=2)
        Button(cal_window, text="x", bg='darkgreen', padx=40, command=lambda: num("*"), **button_config).grid(row=2, column=3)

        # Row 3
        Button(cal_window, text="4", bg='lightcyan', padx=34, command=lambda: num(4), **button_config).grid(row=3, column=0)
        Button(cal_window, text="5", bg='lightcyan', padx=34, command=lambda: num(5), **button_config).grid(row=3, column=1)
        Button(cal_window, text="6", bg='lightcyan', padx=34, command=lambda: num(6), **button_config).grid(row=3, column=2)
        Button(cal_window, text="-", bg='darkgreen', padx=42, command=lambda: num("-"), **button_config).grid(row=3, column=3)

        # Row 4
        Button(cal_window, text="1", bg='lightcyan', padx=34, command=lambda: num(1), **button_config).grid(row=4, column=0)
        Button(cal_window, text="2", bg='lightcyan', padx=34, command=lambda: num(2), **button_config).grid(row=4, column=1)
        Button(cal_window, text="3", bg='lightcyan', padx=34, command=lambda: num(3), **button_config).grid(row=4, column=2)
        Button(cal_window, text="+", bg='darkgreen', padx=40, command=lambda: num("+"), **button_config).grid(row=4, column=3)

        # Row 5
        Button(cal_window, text=".", bg='lightcyan', padx=38, command=lambda: num("."), **button_config).grid(row=5, column=0)
        Button(cal_window, text="0", bg='lightcyan', padx=34, command=lambda: num(0), **button_config).grid(row=5, column=1)
        Button(
            cal_window,
            text="=",
            bg='darkgreen',
            padx=95,
            command=equal,
            **button_config,
        ).grid(row=5, column=2, columnspan=2)

        cal_window.mainloop()


# =================================== Center window =========================================
    def center_window(self, window):
            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height()
            x = (window.winfo_screenwidth() // 2) - (width // 2)
            y = (window.winfo_screenheight() // 2) - (height // 2)
            window.geometry(f'{width}x{height}+{x}+{y}')


#=================================================== About ==================================================

    def show_about(self):
        """Display information about the application"""
        about_text = """ AcaDash
        Version 1.0.0
        
        Developed by: Albert Tandoh
        Released: April 21, 2025
        
        This application is designed to facilitate academic records 
        management in educational institutions. It provides tools 
        for managing student grades, generating reports, and 
        visualizing academic performance data.
        
        Usage Terms:
        • Non-commercial use only
        • Distribution requires explicit permission from the developer
        • Modification without authorization is prohibited
        
        Copyright © 2025 Albert Tandoh
        All Rights Reserved.
        
        Contact:
        For permissions and inquiries, please contact the developer at:
        Tel: +233 59 906 7076
        Email: livin.25@live.com 
        """
        
        about_window = Toplevel(self.root)
        about_window.title("About")
        about_window.geometry("500x500")
        about_window.resizable(False, False)
        # Make window modal
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Add icon to about window
        try:
            icon = self.get_embedded_icon()
            if icon:
                about_window.iconphoto(True, icon)
        except Exception:
            pass
        
        # Create frame with padding
        frame = Frame(about_window, padx=20, pady=20)
        frame.pack(fill=BOTH, expand=True)
        
        
        # Add about text
        text_widget = Text(frame, wrap=WORD, bg='lavender', padx=10, pady=10,
                        font=('inter', 10), height=15)
        text_widget.pack(fill=BOTH, expand=True)
        text_widget.insert('1.0', about_text)
        text_widget.config(state='disabled')
        
        # Add OK button
        Button(frame, text="OK", command=about_window.destroy,
            width=10).pack(pady=(10, 0))
        
        # Center the window on screen
        self.center_window(about_window)



      #======================================== Admin Assignment Section =========================================
    @require_role("admin")
    def assign_class_subject(self):
        """Open a window to assign classes and subjects to users (admin only)"""
        assign_window = Toplevel(self.root)
        assign_window.title("Assign Classes and Subjects")
        assign_window.geometry("450x600")
        assign_window.config(bg="#3B3B3B")
        assign_window.grab_set()

        # Center the window
        self.center_window(assign_window)

        # User Selection
        Label(assign_window, text="Select User (Username):", font=("inter", 12), fg="white", bg="#3B3B3B").grid(
            row=0, column=0, padx=10, pady=10, sticky=W)
        user_combobox = ttk.Combobox(assign_window, width=27, state="readonly")
        user_combobox.grid(row=0, column=1, padx=10, pady=10)

        # Fetch all users from the database
        query = "SELECT id, username FROM users"
        users = self.run_query(query).fetchall()
        user_combobox['values'] = [f"{user[0]} - {user[1]}" for user in users]

        # Create a frame for checkboxes with scrollbar
        checkbox_frame = Frame(assign_window, bg="#3B3B3B")
        checkbox_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky=NSEW)

        # Add canvas and scrollbar
        canvas = Canvas(checkbox_frame, bg="#3B3B3B", highlightthickness=0)
        scrollbar = ttk.Scrollbar(checkbox_frame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas, bg="#3B3B3B")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)
        canvas.configure(yscrollcommand=scrollbar.set)


        Label(assign_window, text="First Name:", bg='#3B3B3B', fg='white', font=('inter', 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
        firstname_entry = Entry(assign_window, width=30)
        firstname_entry.grid(row=1, column=1, padx=10, pady=5)

        Label(assign_window, text="Last Name:", bg='#3B3B3B', fg='white', font=(' inter', 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
        lastname_entry = Entry(assign_window, width=30)
        lastname_entry.grid(row=2, column=1, padx=10, pady=5)


        # Class Selection (Checkboxes)
        Label(assign_window, text="Assign Classes:", font=("inter", 12), fg="white", bg="#3B3B3B").grid(
            row=3, column=0, padx=10, pady=10, sticky=W)

        class_list = ['1Arts1', '1Arts2A', '1Arts2B', '1Arts2C', '1Arts2D', '2Arts1', '2Arts2A', '2Arts2B', '2Arts2C',
                    '2Arts2D', '3Arts1', '3Arts2A', '3Arts2B', '3Arts2C', '3Arts3A', '3Arts3B', '1Agric1', '1Agric2',
                    '2Agric1', '2Agric2', '3Agric1', '3Agric2', '1Bus', '2Bus', '3Bus', '1H/E1', '1H/E2', '2H/E1', '2H/E2',
                    '3H/E1', '3H/E2', '1Sci1', '1Sci2', '2Sci1', '2Sci2', '3Sci1', '3Sci2', '1V/A', '2V/A', '3V/A']

        selected_classes = {}  # Dictionary to store the state of each checkbox
        for i, class_name in enumerate(class_list):
            var = IntVar()
            selected_classes[class_name] = var
            cb = Checkbutton(
                scrollable_frame,
                text=class_name,
                variable=var,
                fg="white",
                bg="#3B3B3B",
                selectcolor="navy",
                activebackground="white",
                activeforeground="#3B3B3B",
                font=("inter", 10),
                relief=FLAT,
                cursor="hand2"
            )
            cb.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky=W)

        # Configure the canvas and scrollbar
        canvas.grid(row=0, column=0, sticky=NSEW)
        scrollbar.grid(row=0, column=1, sticky=NS)
        checkbox_frame.grid_rowconfigure(0, weight=1)
        checkbox_frame.grid_columnconfigure(0, weight=1)

        # Subject Selection
        Label(assign_window, text="Assign Subject:", font=("inter", 12), fg="white", bg="#3B3B3B").grid(
            row=6 + len(class_list) // 3, column=0, padx=10, pady=10, sticky=W)
        
        subject_list = ['Acounting', 'Animal Husb.', 'Biology', 'Bus. Mgmt.', 'Chemistry', 'Costing', 'Crop Husb.',
                        'CRS', 'English', 'Economics', 'Elective Maths.', 'Foods & Nut.', 'French', 'General Agric',
                        'Geography', 'Government', 'GKA', 'Graphic Design', 'Integrated Sci.', 'Leather Work',
                        'Mathematics', 'Mgmt-in-Living', 'Physics', 'Social Studies', 'Twi']
        
        subject_combobox = ttk.Combobox(assign_window, width=27, state="readonly")
        subject_combobox['values'] = subject_list
        subject_combobox.grid(row=6 + len(class_list) // 3, column=1, padx=10, pady=10)

        # Assign Button
        Button(
            assign_window,
            text="Assign",
            command=lambda: self.save_assignment(
                user_combobox.get(),
                firstname_entry.get(),
                lastname_entry.get(),
                selected_classes,
                subject_combobox.get(),
                assign_window
            ),
            bg="green",
            fg="white",
            font=("inter", 10, "bold")
        ).grid(row=7 + len(class_list) // 3, column=1, pady=20, sticky=E)

#======================================== Save Assignment =========================================
    @db_error_handler
    def save_assignment(self, user, fname, lname, selected_classes, subject, window):
        """Save the assigned classes and subject to the database with duplicate check"""
        if not user or not subject:
            self.show_message("Warning", "All fields are required.", "warning")
            return

        user_parts = user.split(" - ")
        user_id = user_parts[0]

        # Get selected classes
        assigned_classes = [class_name for class_name, var in selected_classes.items() if var.get() == 1]
        if not assigned_classes:
            self.show_message("Error", "Please select at least one class.", "error")
            return

        # Insert teacher only if not already present
        teacher_exists = self.run_query("SELECT 1 FROM teachers WHERE user_id = ?", (user_id,)).fetchone()
        if not teacher_exists:
            self.run_query("INSERT INTO teachers (user_id, fname, lname) VALUES (?, ?, ?)", (user_id, fname, lname))

        # Track duplicates
        duplicates = []

        for class_name in assigned_classes:
            # Check if assignment already exists
            existing = self.run_query(
                "SELECT 1 FROM assignments WHERE user_id = ? AND class = ? AND subject = ?",
                (user_id, class_name, subject)
            ).fetchone()

            if existing:
                duplicates.append(class_name)
                continue

            # Insert assignment
            self.run_query(
                "INSERT INTO assignments (user_id, class, subject) VALUES (?, ?, ?)",
                (user_id, class_name, subject)
            )

        if duplicates:
            dup_text = ", ".join(duplicates)
            self.show_message("Warning", f"Skipped existing assignments for: {dup_text}", "warning")

        self.show_message("Success", "Assignments processed successfully!", "success")
        window.destroy()



    def fetch_user_assignments(self, user_id):
        """
        Fetch assigned classes, subjects, and teacher info for a specific user_id
        """
        query = """
            SELECT 
                a.class, 
                a.subject, 
                t.fname, 
                t.lname
            FROM assignments a
            JOIN teachers t ON a.user_id = t.user_id
            WHERE a.user_id = ?
        """
        result = self.run_query(query, (user_id,)).fetchall()
        return result

#============================================ Delete Assignment ===========================================
    def open_delete_assignment_window(self):
        """Open a window for the admin to delete an assignment record or delete the user entirely."""
        if self.current_user_role != "admin":
            self.show_message("Access Denied", "Only admins can delete assignments.", "warning")
            return

        window = Toplevel(self.root)
        window.title("Delete Assignment or User")
        window.geometry("420x330")
        window.config(bg="#3B3B3B")
        window.grab_set()
        self.center_window(window)

        # User Dropdown
        Label(window, text="Select User:", bg="#3B3B3B", fg="white",font=("inter", 10)).grid(row=0, column=0, padx=10, pady=10, sticky=W)
        user_combobox = ttk.Combobox(window, state="readonly", width=20)
        user_combobox.grid(row=0, column=1, padx=10, pady=10)

        users = self.run_query("SELECT id, username FROM users").fetchall()
        user_combobox['values'] = [f"{u[0]} - {u[1]}" for u in users]

        # Class Entry
        Label(window, text="Class:", bg="#3B3B3B", fg="white",font=("inter", 10)).grid(row=1, column=0, padx=10, pady=10, sticky=W)
        class_combobox = ttk.Combobox(window, state = "readonly", width=20)
        class_combobox.grid(row=1, column=1, padx=10, pady=10)

        classes = self.run_query("SELECT DISTINCT class FROM assignments").fetchall()
        class_combobox['values'] = [c[0] for c in classes]



        # Subject Entry
        Label(window, text="Subject:", bg="#3B3B3B", fg="white", font=("inter", 10)).grid(row=2, column=0, padx=10, pady=10, sticky=W)
        subject_combobox = ttk.Combobox(window, state="readonly", width=20)
        subject_combobox.grid(row=2, column=1, padx=10, pady=10)

        subjects = self.run_query("SELECT DISTINCT subject FROM assignments").fetchall()
        subject_combobox['values'] = [s[0] for s in subjects]


        # Delete Assignment Button
        Button(
            window, text="Delete Assignment",
            bg="crimson", fg="white", font=("inter", 10, "bold"),
            command=lambda: self.delete_assignment(
                user_combobox.get(), class_combobox.get(), subject_combobox.get(), window
            )
        ).grid(row=3, column=1, padx=10, pady=10, sticky=E)

        # Divider
        Label(window, text="— OR —", bg="#3B3B3B", fg="gray").grid(row=4, column=1, pady=5)

        # Delete User Button
        Button(
            window, text="Delete Entire User & Assignments",
            bg="darkred", fg="white", font=("inter", 10, "bold"),
            command=lambda: self.delete_user_and_assignments(user_combobox.get(), window)
        ).grid(row=5, column=1, padx=10, pady=10, sticky=E)

    
    def delete_assignment(self, user_combo, class_combo, subject_combo, window):
        if not user_combo or not class_combo or not subject_combo:
            self.show_message("Missing Info", "Please fill all fields.", "warning")
            return

        user_id = user_combo.split(" - ")[0].strip()
        class_name = class_combo.split(" - ")[-1].strip()
        subject = subject_combo.split(" - ")[-1].strip()


        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Delete assignment: {class_name} - {subject} for this user?"
          )
        if not confirm:
            return

        try:
            query = "DELETE FROM assignments WHERE user_id = ? AND class = ? AND subject = ?"
            self.run_query(query, (user_id, class_name, subject))
            self.show_message("Success", "Assignment deleted successfully!", "success")
            window.destroy()
        except Exception as e:
            self.show_message("Error", f"An error occurred: {e}", "error")



    def delete_user_and_assignments(self, user_combo, window):
        """Delete a user and all related assignments and teacher record."""
        if not user_combo:
            self.show_message("Missing Info", "Please select a user.", "warning")
            return

        user_id = user_combo.split(" - ")[0]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            "This will delete the user and all their assignments. Continue?"
        )
        if not confirm:
            return

        try:
            # Delete from assignments
            self.run_query("DELETE FROM assignments WHERE user_id = ?", (user_id,))
            # Delete from teachers
            self.run_query("DELETE FROM teachers WHERE user_id = ?", (user_id,))
            # Delete from users
            self.run_query("DELETE FROM users WHERE id = ?", (user_id,))
            
            self.show_message("Success", "User and all assignments deleted.", "success")
            window.destroy()
        except Exception as e:
            self.show_message("Error", f"Could not delete user: {e}", "error")


#==================================== Search teacher subject and classess =========================================
    def open_search_teacher_window(self):
        """Open a window to search and display teacher assignment info."""
        window = Toplevel(self.root)
        window.title("Search Teacher Info")
        window.geometry("700x500")
        window.config(bg="#3B3B3B")
        self.center_window(window)
        window.grab_set()

        # Title
        Label(
            window,
            text="Search Teacher Assignments",
            bg="#3B3B3B",
            fg="white",
            font=("inter", 14, "bold")
        ).pack(pady=10)

        # Search Entry Frame
        search_frame = Frame(window, bg="#3B3B3B")
        search_frame.pack(pady=10)

        Label(
            search_frame,
            text="Enter First or Last Name:",
            bg="#3B3B3B",
            fg="white",
            font=("inter", 10)
        ).pack(side=LEFT, padx=5)

        search_entry = Entry(search_frame, width=30)
        search_entry.pack(side=LEFT, padx=5)

        # Results Treeview
        columns = ("User ID", "First Name", "Last Name", "Subject", "Class")
        results_tree = ttk.Treeview(window, columns=columns, show="headings")

        for col in columns:
            results_tree.heading(col, text=col)
            results_tree.column(col, width=130, anchor="center")

        results_tree.pack(pady=20, fill=BOTH, expand=True)

        # Search Button
        Button(
            search_frame,
            text="Search",
            command=lambda: self.perform_teacher_search(search_entry.get(), results_tree),
            bg="navy",
            fg="white",
            font=("inter", 10)
        ).pack(side=LEFT, padx=5)

        # Delete Button
        Button(
            window,
            text="Delete Selected",
            bg="red",
            fg="white",
            font=("inter", 10, "bold"),
            command=lambda: self.delete_selected_assignment(results_tree)
        ).pack(pady=10)


    def perform_teacher_search(self, search_term, treeview):
        """Perform search based on teacher's first or last name and update treeview."""
        treeview.delete(*treeview.get_children())  # Clear existing rows

        query = """
            SELECT t.user_id, t.fname, t.lname, a.subject, a.class
            FROM teachers t
            JOIN assignments a ON a.user_id = t.user_id
            WHERE t.fname LIKE ? OR t.lname LIKE ?
        """
        search_term = search_term.strip()
        params = (f"%{search_term}%", f"%{search_term}%")
        results = self.run_query(query, params).fetchall()

        if results:
            for row in results:
                treeview.insert("", "end", values=row)
        else:
            self.show_message("No Results", "No matching teacher found.", "info")


    def delete_selected_assignment(self, tree):
        """Delete selected assignment from Treeview and database"""
        selected_item = tree.selection()
        if not selected_item:
            self.show_message("No selection", "Please select a record to delete.", "warning")
            return

        try:
            values = tree.item(selected_item)["values"]
            user_id, _, _, subject, class_name = values
        except Exception:
            self.show_message("Error", "Could not retrieve selected data.", "error")
            return

        confirm = messagebox.askyesno("Confirm Deletion", f"Delete assignment: {class_name} - {subject}?")
        if not confirm:
            return

        try:
            query = "DELETE FROM assignments WHERE user_id = ? AND class = ? AND subject = ?"
            self.run_query(query, (user_id, class_name, subject))
            tree.delete(selected_item)
            self.show_message("Deleted", "Assignment removed successfully.", "info")
        except Exception as e:
            self.show_message("Error", f"Could not delete assignment: {e}", "error")



#================================================== Login window ==============================================

    def login(self):
        """Display the login window with the logo and Remember Me option"""
        login_window = Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("450x550")
        login_window.resizable(False, False)
        login_window.config(bg="#3B3B3B")

        # Center the login window
        self.center_window(login_window)

        # Add the logo to the login window
        logo_canvas = Canvas(
            login_window,
            width=180,
            height=180,
            bg='navy',
            bd=2,
            relief=RIDGE
        )
        logo_canvas.grid(row=0, column=0, columnspan=3, padx=120, pady=(20, 5))
        
        # Adjusted Y coordinate (move everything up)
        y_offset = -10  # negative value to move up

        # Updated center point
        x, y = 90, 90 + y_offset

        # Draw logo elements shifted upward
        logo_canvas.create_oval(20, 20 + y_offset, 160, 160 + y_offset, fill='navy', outline='white', width=2)
        logo_canvas.create_oval(30, 30 + y_offset, 150, 150 + y_offset, fill='#1A1A40', outline='royalblue', width=2)

        logo_canvas.create_text(x - 10, y, text="Aca", fill='white', font=('Helvetica', 18, 'italic bold'), anchor='e')
        logo_canvas.create_text(x - 10, y, text="Dash", fill='#FF6F61', font=('Helvetica', 18, 'italic bold'), anchor='w')

        
        # Draw an inverted open book symbol ABOVE the text
        book_y = y - 15  # Raise book above the EduDash text

        # Book base (spine) – inverted "V" shape
        logo_canvas.create_line(x - 15, book_y - 10, x, book_y, fill='white', width=4)
        logo_canvas.create_line(x, book_y, x + 15, book_y - 10, fill='white', width=4)

        # Keep the descriptions at the bottom
        logo_canvas.create_text(90, 170 + y_offset, text="Your smart ", fill='white', font=('Inter', 10, 'italic bold') )
        logo_canvas.create_text(90, 185 + y_offset, text="academic dashboard", fill='#FF6F61', font=('Inter', 10, 'italic bold'))


        # Username and Password Labels and Entry Fields
        Label(login_window, text="Username:", font=("inter", 12),fg = "white", bg="#3B3B3B").grid(row=1, column=0, padx=(40, 10), pady=(20, 5), sticky=W)
        username_entry = Entry(login_window, width=30)
        username_entry.grid(row=1, column=1, padx=10, pady=(20,5), sticky=W)

        Label(login_window, text="Password:", font=("inter", 12), fg = "white",bg="#3B3B3B").grid(row=2, column=0, padx=(40, 10), pady=(5, 5), sticky=W)
        password_entry = Entry(login_window, width=30, show="*")
        password_entry.grid(row=2, column=1, padx=10, pady=(5,5), sticky=W) 

        # Remember Me Checkbox
        remember_me_var = IntVar()
        remember_me_checkbox = Checkbutton(
            login_window,
            text="Remember Me",
            variable=remember_me_var,
            fg="orange",
            bg="#3B3B3B",
            font=("inter", 10),
            selectcolor="lavender",
        )
        remember_me_checkbox.grid(row=3, column=1, sticky=W, pady=(5, 15))

        # Load remembered username
        try:
            with open("remember_me.txt", "r") as file:
                remembered_username = file.read().strip()
                username_entry.insert(0, remembered_username)
        except FileNotFoundError:
            pass

        # Login Button
        Button(
            login_window,
            text="Login",
            command=lambda: self.authenticate_user(
                username_entry.get(),
                password_entry.get(),
                login_window,
                remember_me_var.get()
            ),
            bg="green",
            fg="white",
            font=("inter", 11, "bold")
        ).grid(row=4, column=1, pady=20)

        # Exit Button
        Button(
            login_window,
            text="Exit",
            command=lambda: self.exit_application(login_window),
            bg="red",
            fg="white",
            font=("inter", 11, "bold")
        ).grid(row=5, column=1, pady=5)
      

        # Forgot Password Button
        Button(
            login_window,
            text="Forgot Password",
            command=self.forgot_password,
            bg="blue",
            fg="white",
            font=("inter", 11, "bold"),
            relief=FLAT
        ).grid(row=6, column=1, pady=10, sticky=W)
   
     #===========================  Exit Application ============================
    def exit_application(self, login_window):
        """Exit the application from the login window"""
        login_window.destroy()  # Close the login window
        self.root.destroy()  # Close the main application


    #======================================== Sign Up  =========================================
    @require_role("admin")
    def sign_up(self):
        """Display the sign-up window (admin only)"""
        sign_up_window = Toplevel(self.root)
        sign_up_window.title("Sign Up")
        sign_up_window.geometry("400x300")
        sign_up_window.config(bg="#3B3B3B")
        sign_up_window.grab_set()
        # Center the sign-up window
        self.center_window(sign_up_window)

        # Username, Password, and Role Fields
        Label(sign_up_window, text="Username:", font=("inter", 12), fg="white", bg="#3B3B3B").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        username_entry = Entry(sign_up_window, width=30)
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(sign_up_window, text="Password:", font=("inter", 12), fg="white", bg="#3B3B3B").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        password_entry = Entry(sign_up_window, width=30, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(sign_up_window, text="Confirm Password:", font=("inter", 12), fg="white", bg="#3B3B3B").grid(row=2, column=0, padx=10, pady=10, sticky=W)
        confirm_password_entry = Entry(sign_up_window, width=30, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)


        # Sign-Up Button
        Button(
            sign_up_window,
            text="Sign Up",
            command=lambda: self.register_user(
                username_entry.get(),
                password_entry.get(),
                confirm_password_entry.get(), # Pass the selected role
                sign_up_window  # Pass the sign-up window
            ),
            bg="green",
            fg="white",
            font=("inter", 10, "bold")
        ).grid(row=4, column=1, pady=20, sticky=E)

    #=================================== Register User ========================================= 

    def register_user(self, username, password, confirm_password, role ,window):
        """Register a new user with a specific role"""
        if not username or not password or not confirm_password or not role:
            self.show_message("Warning", "All fields are required.", "warning")
            return

        if password != confirm_password:
            self.show_message("Info", "Passwords do not match.", "info")
            return

        # Hash the password for security
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            self.run_query(query, (username, hashed_password, role))
            self.show_message("Success", "User registered successfully!", "success")
            window.destroy()  # Close the sign-up window
        except sqlite3.IntegrityError:
            self.show_message("Info", "Username already exists. Please choose a different username.", "info")


    #======================================== Logout =========================================
    def logout(self):
        """Log out the current user and return to the login screen"""
        confirm = messagebox.askquestion("Logout", "Are you sure you want to log out")
        if confirm == "yes":
            self.root.withdraw()  # Hide the main window
            self.login()  # Show the login window

        
#========================================= Password Change =========================================
    def change_password(self):
        """Open a window to change the password for the logged-in user"""
        change_password_window = Toplevel(self.root)
        change_password_window.title("Change Password")
        change_password_window.geometry("400x300")
        change_password_window.config(bg="#3B3B3B")
        change_password_window.resizable(False, False)
        change_password_window.grab_set()
        # Center the window
        self.center_window(change_password_window)

        
        Label(change_password_window, text="Current Password:", font=("inter", 12),fg="white", bg="#3B3B3B").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        current_password_entry = Entry(change_password_window, width=30, show="*")
        current_password_entry.grid(row=0, column=1, padx=10, pady=10)

        Label(change_password_window, text="New Password:", font=("inter", 12), fg="white",bg="#3B3B3B").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        new_password_entry = Entry(change_password_window, width=30, show="*")
        new_password_entry.grid(row=1, column=1, padx=10, pady=10)

        Label(change_password_window, text="Confirm New Password:", font=("inter", 12),fg="white", bg="#3B3B3B").grid(row=2, column=0, padx=10, pady=10, sticky=W)
        confirm_password_entry = Entry(change_password_window, width=30, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Change Password Button
        Button(
            change_password_window,
            text="Change Password",
            command=lambda: self.update_password(
                current_password_entry.get(),
                new_password_entry.get(),
                confirm_password_entry.get(),
                change_password_window
            ),
            bg="green",
            fg="white",
            font=("inter", 10, "bold")
        ).grid(row=3, column=1, pady=20, sticky=E)

   #======================================== Update Password =========================================
    def update_password(self, current_password, new_password, confirm_password, window):
        """Update the password for the logged-in user"""
        try:
            # Validate inputs
            if not current_password or not new_password or not confirm_password:
                self.show_message("Warning", "All fields are required.", "warning")
                return

            if new_password != confirm_password:
                self.show_message("Info", "New password and confirmation do not match.", "info")
                return

            # Hash the current password for comparison
            hashed_current_password = hashlib.sha256(current_password.encode()).hexdigest()

            # Check if the current password is correct
            query = "SELECT password FROM users WHERE username = ?"
            result = self.run_query(query, (self.logged_in_username,)).fetchone()
            if not result or result[0] != hashed_current_password:
                self.show_message("Info", "Current password is incorrect.", "info")
                return

            # Hash the new password
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

            # Update the password in the database
            update_query = "UPDATE users SET password = ? WHERE username = ?"
            self.run_query(update_query, (hashed_new_password, self.logged_in_username))

            self.show_message("Success", "Password updated successfully!", "success")
            window.destroy()  # Close the change password window

        except Exception as e:
            self.show_message("Error", f"An error occurred: {e}", "error")

    #======================================== Forgot Password =========================================
    def forgot_password(self):
        """Open a window to reset the password"""
        forgot_password_window = Toplevel(self.root)
        forgot_password_window.title("Forgot Password")
        forgot_password_window.geometry("400x300")
        forgot_password_window.config(bg="#3B3B3B")
        forgot_password_window.resizable(False, False)
       

        # Center the window
        self.center_window(forgot_password_window)

        # Username Entry
        Label(forgot_password_window, text="Enter Username:", font=("inter", 12),fg="white", bg="#3B3B3B").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        username_entry = Entry(forgot_password_window, width=30)
        username_entry.grid(row=0, column=1, padx=10, pady=10)

        # New Password Entry
        Label(forgot_password_window, text="New Password:", font=("inter", 12), fg="white",bg="#3B3B3B").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        new_password_entry = Entry(forgot_password_window, width=30, show="*")
        new_password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Confirm Password Entry
        Label(forgot_password_window, text="Confirm Password:", font=("inter", 12), fg="white",bg="#3B3B3B").grid(row=2, column=0, padx=10, pady=10, sticky=W)
        confirm_password_entry = Entry(forgot_password_window, width=30, show="*")
        confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

        # Reset Password Button
        Button(
            forgot_password_window,
            text="Reset Password",
            command=lambda: self.reset_password(
                username_entry.get(),
                new_password_entry.get(),
                confirm_password_entry.get(),
                forgot_password_window
            ),
            bg="green",
            fg="white",
            font=("inter", 10, "bold")
        ).grid(row=3, column=1, pady=20, sticky=E)


    #======================================== Reset Password =========================================
    def reset_password(self, username, new_password, confirm_password, window):
        """Reset the password for a user"""
        if not username or not new_password or not confirm_password:
            self.show_message("Warning", "All fields are required.", "warning")
            return

        if new_password != confirm_password:
            self.show_message("Error", "New password and confirmation do not match.", "error")
            return

        # Hash the new password
        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

        # Update the password in the database
        query = "UPDATE users SET password = ? WHERE username = ?"
        result = self.run_query(query, (hashed_new_password, username))

        if result.rowcount == 0:
            self.show_message("Error", "Username not found.", "error")
        else:
            self.show_message("Success", "Password reset successfully!", "success")
            window.destroy()

   #======================================== Authenticate User =========================================
    def authenticate_user(self, username, password, login_window, remember_me):
        """Authenticate the user and store their role and assignments"""
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT id, role FROM users WHERE username = ? AND password = ?"
            result = self.run_query(query, (username, hashed_password)).fetchone()

            if result:
                user_id, self.current_user_role = result  # Store the user? ID and role
                self.logged_in_username = username  # Store the logged-in user? username

                # Save username if "Remember Me" is checked
                if remember_me:
                    with open("remember_me.txt", "w") as file:
                        file.write(username)
                else:
                    # Clear the remembered username
                    if os.path.exists("remember_me.txt"):
                        os.remove("remember_me.txt")

                if self.current_user_role == "user":
                    self.user_assignments = self.fetch_user_assignments(user_id)  # Fetch assignments for users
                else:
                    self.user_assignments = None  # Admins have full access
                
                self.create_menu_bar() 
                login_window.destroy()  # Close the login window
                self.root.deiconify()
                self.populate_class_subject_comboboxes(self.class_combobox, self.subject_combobox) 
                self.show_message(
                    "Welcome",
                     f"Welcome, {username}! to AcaDash. \nVisualize, Track, and Manage Academic Performance your students effortlessly.", 
                     "success"
                ) 
            else:
                self.show_message("Login Failed", "Invalid username or password. Please try again.", "error")
                   
        except Exception as e:
            self.show_message(
                f"Login failed: {str(e)}",
                "error"
            )

            

#========================================Update combobox based on assignment=============================
    def populate_class_subject_comboboxes(self, class_cb, subject_cb):
        """Populate class and subject comboboxes based on user role/assignments."""
        if self.current_user_role == "admin":
            class_list = [
                '1Arts1', '1Arts2A', '1Arts2B', '1Arts2C', '1Arts2D', '2Arts1', '2Arts2A', '2Arts2B', '2Arts2C',
                '2Arts2D', '3Arts1', '3Arts2A', '3Arts2B', '3Arts2C', '3Arts3A', '3Arts3B', '1Agric1', '1Agric2',
                '2Agric1', '2Agric2', '3Agric1', '3Agric2', '1Bus', '2Bus', '3Bus', '1H/E1', '1H/E2', '2H/E1', '2H/E2',
                '3H/E1', '3H/E2', '1Sci1', '1Sci2', '2Sci1', '2Sci2', '3Sci1', '3Sci2', '1V/A', '2V/A', '3V/A'
            ]
            subject_list = [
                'Acounting', 'Animal Husb.', 'Biology', 'Bus. Mgmt.', 'Chemistry', 'Costing', 'Crop Husb.', 'CRS', 'English',
                'Economics', 'Elective Maths.', 'Foods & Nut.', 'French', 'General Agric', 'Geography', 'Government', 'GKA',
                'Graphic Design', 'Integrated Sci.', 'Leather Work', 'Mathematics', 'Mgmt-in-Living', 'Physics', 'Social Studies', 'Twi'
            ]
        elif self.current_user_role == "user":
            assigned_classes = list(set(assignment[0] for assignment in self.user_assignments))
            assigned_subjects = list(set(assignment[1] for assignment in self.user_assignments))
            class_list = assigned_classes
            subject_list = assigned_subjects
        else:
            class_list = []
            subject_list = []

        class_cb['values'] = class_list
        subject_cb['values'] = subject_list
        if class_list:
            class_cb.set("Choose Class")
        if subject_list:
            subject_cb.set("Choose Subject")
            
        


#======================================= Message Box ==================================================
    def show_message(self, title, message, message_type="info", duration=10000):
        """Enhanced message display with automatic cleanup"""
        if hasattr(self, 'message'):
            self.message["text"] = message
            color_map = {
                "error": "red",
                "warning": "orange",
                "success": "green",
                "info": "blue"
            }
            self.message["fg"] = color_map.get(message_type, "black")
            self.message.after(duration, lambda: self.message.configure(text=""))
        
        # Show messagebox for important messages
        if message_type in ["error", "warning"]:
            messagebox.showerror(title, message) if message_type == "error" else messagebox.showwarning(title, message)
    

    #======================================== User Table in Database =========================================
    def create_user_table(self):
        """Create a table for storing user credentials and roles"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user')) DEFAULT 'user'
        )
        """
        self.run_query(query)

    
    #========================================Create an Assignment Table ===========================
    
    def create_assignment_table(self):
        """Create a table for storing class and subject assignments"""
        query = """
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            class TEXT NOT NULL,
            subject TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        self.run_query(query)

    
    
    def create_academic_records_table(self):
        query = """ 
        CREATE TABLE IF NOT EXISTS academic_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            sch_code TEXT NOT NULL DEFAULT '0040801',
            student_num TEXT NOT NULL,
            index_num TEXT NOT NULL,
            class_ TEXT,
            year VARCHAR(10) NOT NULL,
            period VARCHAR(8) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES student_records(id)
        )
        """
        self.run_query(query, ())


    # ================================== Add records to academic table  ==================================================
    def add_academic_record_window(self):
        window = Toplevel(self.root)
        window.title("Add Academic Record")
        window.geometry("400x350")
        window.configure(bg="#2F2F2F")
        self.center_window(window)
        window.grab_set()


        fields = {
            "First Name": StringVar(),
            "Last Name": StringVar(),
            "Year": StringVar(),
            "Period": StringVar()
        }

        entry_widgets = {}

        for idx, (label, var) in enumerate(fields.items()):
            Label(window, text=label + ":", bg="#2F2F2F", fg="white").grid(row=idx, column=0, padx=10, pady=5, sticky=W)
            entry = Entry(window, textvariable=var, width=30)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entry_widgets[label] = entry

        # Add placeholders to Year and Period
        self.set_placeholder(entry_widgets["Year"], "e.g. 2024/2025")
        self.set_placeholder(entry_widgets["Period"], "e.g. Term1 or Sem1")

        def save_record():
            fname = fields["First Name"].get().strip()
            lname = fields["Last Name"].get().strip()
            year = fields["Year"].get().strip()
            period = fields["Period"].get().strip()

            if year == "e.g. 2024/2025":
                year = ""
            if period == "e.g. Term1 or Sem1":
                period = ""

            if not all([fname, lname, year, period]):
                self.show_message("Missing Info", "Please fill all fields.", "warning")
                return

            student_query = """
                SELECT id FROM students_records
                WHERE fname = ? AND lname = ?
                LIMIT 1
            """
            student_result = self.run_query(student_query, (fname, lname)).fetchone()

            if not student_result:
                self.show_message("Not Found", f"No student found for {fname} {lname}.", "error")
                return

            student_id = student_result[0]
            prefix = lname[0].upper()

            num_query = """
                SELECT student_num FROM academic_records
                WHERE student_num LIKE ?
                ORDER BY student_num DESC LIMIT 1
            """
            row = self.run_query(num_query, (f"{prefix}%",)).fetchone()
            if row and row[0]:
                try:
                    last_num = int(row[0][1:])
                    student_num = f"{prefix}{last_num + 1:03d}"
                except ValueError:
                    student_num = f"{prefix}001"
            else:
                student_num = f"{prefix}001"

            sch_code = '0040801'
            index_num = f"{sch_code}{student_num}"

            insert_query = """
                INSERT INTO academic_records (student_id, sch_code, student_num, index_num, year, period)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            params = (student_id, sch_code, student_num, index_num, year, period)
            self.run_query(insert_query, params)

            self.show_message("Success", f"Academic record added for {fname} {lname} ({student_num}).", "info")
            window.destroy()

        Button(window, text="Save Record", command=save_record, bg="green", fg="white").grid(row=6, column=1, pady=20)

    # ==== Add these utility methods to your class ====

    def set_placeholder(self, entry, placeholder, color='grey'):
        entry.insert(0, placeholder)
        entry.config(fg=color)
        entry.bind("<FocusIn>", lambda e: self.clear_placeholder(entry, placeholder))
        entry.bind("<FocusOut>", lambda e: self.restore_placeholder(entry, placeholder, color))

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, 'end')
            entry.config(fg='black')

    def restore_placeholder(self, entry, placeholder, color='grey'):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg=color)

#=============================================================================================================================
    def show_records_window(self):
        """Open a window to retrieve student data based on Class, Subject, Year, and Period."""
        win = Toplevel(self.root)
        win.title("Retrieve Student Records")
        win.geometry("900x500")
        win.configure(bg="#2E2E2E")
        self.center_window(win)
        win.grab_set()

        row_frame = Frame(win, bg="#2E2E2E")
        row_frame.grid(row=0, column=0, columnspan=8, pady=10)

        # --- Class ---
        class_frame = Frame(row_frame, bg="#2E2E2E")
        class_frame.pack(side=LEFT, padx=10)
        Label(class_frame, text="Class:", bg="#2E2E2E", fg="white").pack(side=LEFT)
        class_cb = ttk.Combobox(class_frame, width=15, state="readonly")
        class_cb.pack(side=LEFT)
        

        # --- Subject ---
        subject_frame = Frame(row_frame, bg="#2E2E2E")
        subject_frame.pack(side=LEFT, padx=10)
        Label(subject_frame, text="Subject:", bg="#2E2E2E", fg="white").pack(side=LEFT)
        subject_cb = ttk.Combobox(subject_frame, width=15, state="readonly")
        subject_cb.pack(side=LEFT)
        subject_cb.set("Select")


        # Populate class and subject comboboxes based on user role
        self.populate_class_subject_comboboxes(class_cb, subject_cb)

        # --- Year ---
        year_frame = Frame(row_frame, bg="#2E2E2E")
        year_frame.pack(side=LEFT, padx=10)
        Label(year_frame, text="Year:", bg="#2E2E2E", fg="white").pack(side=LEFT)
        year_entry = Entry(year_frame, width=14)
        year_entry.insert(0, "2024/2025")
        year_entry.pack(side=LEFT)
        

        # --- Period ---
        periods_list =["Sem1", "Sem2", "Term1", "Term2", "Term3"]
        period_frame = Frame(row_frame, bg="#2E2E2E")
        period_frame.pack(side=LEFT, padx=10)
        Label(period_frame, text="Period:", bg="#2E2E2E", fg="white").pack(side=LEFT)
        period_cb = ttk.Combobox(period_frame, values=periods_list, width=12, state="readonly")
        period_cb.pack(side=LEFT)
        period_cb.set("Choose")

        # --- Treeview ---
        cols = ("ID","Index Number", "First Name", "Last Name", "Total Score", "Grade")
        tree_frame = Frame(win)
        tree_frame.grid(row=2, column=0, columnspan=8, padx=5, pady=10, sticky="nsew")

        tree_scroll = Scrollbar(tree_frame)
        tree_scroll.pack(side=RIGHT, fill=Y)

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)

        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=130)

        tree.pack(fill=BOTH, expand=True)

        win.grid_rowconfigure(2, weight=1)
        win.grid_columnconfigure(0, weight=1)

        # --- Fetch Function ---
        def fetch_records():
            class_ = class_cb.get()
            subject = subject_cb.get()
            year = year_entry.get().strip()
            period = period_cb.get().strip()

            if not all([class_, subject, year, period]):
                self.show_message("Warning", "Please fill all fields.", "warning")
                return

            query = """
                SELECT a.student_id, a.index_num, s.fname, s.lname, s.totalScore, s.grade
                FROM academic_records a
                JOIN students_records s ON s.id = a.student_id
                WHERE s.class_ = ? AND s.subject = ? AND a.year = ? AND a.period = ?
                ORDER BY s.totalScore DESC
            """
            results = self.run_query(query, (class_, subject, year, period)).fetchall()

            # Clear existing data
            for row in tree.get_children():
                tree.delete(row)

            if not results:
                self.show_message("Info", "No records found.", "info")
                return

            for row in results:
                tree.insert("", "end", values=row)

        # --- Save to PDF ---
        def save_to_pdf():
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if not file_path:
                return

            try:
                class_ = class_cb.get()
                subject = subject_cb.get()
                year = year_entry.get().strip()
                period = period_cb.get().strip()

                c = canvas.Canvas(file_path, pagesize=A4)
                width, height = A4
                c.setFont("Helvetica-Bold", 14)
                c.drawString(180, height - 40, "Student Academic Records")

                # Header Info
                c.setFont("Helvetica", 11)
                c.drawString(50, height - 60, f"Class: {class_}   Subject: {subject}   Year: {year}   Period: {period}")

                # Table Headers
                c.setFont("Helvetica-Bold", 10)
                y = height - 90
                headers = ["ID","Index Number", "First Name", "Last Name", "Total Score", "Grade"]
                for i, header in enumerate(headers):
                    c.drawString(50 + i * 100, y, header)

                # Table Data
                y -= 20
                c.setFont("Helvetica", 10)
                for child in tree.get_children():
                    values = tree.item(child)["values"]
                    for i, val in enumerate(values):
                        c.drawString(50 + i * 100, y, str(val))
                    y -= 20
                    if y < 50:
                        c.showPage()
                        y = height - 50

                c.save()
                self.show_message("Success", "PDF saved successfully.", "success")
            except Exception as e:
                self.show_message("Error", f"Failed to save PDF: {e}", "error")

        # --- Buttons ---
        Button(win, text="Show Records", command=fetch_records, bg="blue", fg="white").grid(row=1, column=5, pady=10)
        Button(win, text="Save to PDF", command=save_to_pdf, bg="green", fg="white").grid(row=1, column=6, pady=10)

    
    #============================================= Add records to previous entry =================== ======
    @db_error_handler
    def update_academic_records_for_previous_entries(self, year, period):
        # Fetch students that don't have a corresponding record in academic_records
        students_without_academic = self.run_query("""
            SELECT sr.id, sr.fname, sr.lname, sr.class_
            FROM students_records sr
            LEFT JOIN academic_records ar
            ON sr.id = ar.student_id
            WHERE ar.student_id IS NULL
        """)
        rows = students_without_academic.fetchall()

        # Loop through each student and add missing records to academic_records
        for row in rows:
            student_id = row[0]
            fname = row[1]
            lname = row[2]
            class_ = row[3]

            # Generate student_num
            prefix = lname[0].upper()
            latest = self.run_query("""
                SELECT student_num FROM academic_records
                WHERE student_num LIKE ?
                ORDER BY student_num DESC LIMIT 1
            """, (f"{prefix}%",))
            last_row = latest.fetchone()

            if last_row and last_row[0]:
                try:
                    last_num = int(last_row[0][1:])
                    student_num = f"{prefix}{last_num + 1:03d}"
                except:
                    student_num = f"{prefix}001"
            else:
                student_num = f"{prefix}001"

            # Generate index_num using a fixed school code
            sch_code = "0040801"
            index_num = f"{sch_code}{student_num}"

            # Insert the missing academic record
            self.run_query("""
                INSERT INTO academic_records (sch_code, student_num, index_num, student_id, year, period)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sch_code, student_num, index_num, student_id, year, period))

            self.show_message("Success", "Academic records updated successfully for previous students!", "success")
    
    
    #================================================ Main Function =========================================

if __name__ == "__main__":
    root = Tk()
    
    # Get screen dimensions
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Calculate window size (85% of screen size)
    window_width = min(int(screen_width * 0.85), 1600)
    window_height = min(int(screen_height * 0.85), 800)
    
    # Calculate center position
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    
    # Set window size and position
    root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
    
    # Make window resizable
    root.resizable(True, True)
    
    # Adjust minimum size for smaller screens
    root.minsize(1100, 650)

    # Hide the main window initially
    root.withdraw()
    
    # Create the application instance
    application = School_Portal(root)
    
    application.login()  # Show the login window
    
    root.mainloop()

