from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
import time 
import csv
from tkinter.filedialog import asksaveasfilename
from tkinter import filedialog
import os


class School_Portal:
    db_name = "students.db"


    def __init__(self, root):
        self.root = root
        self.root.title("Student Database Management System")
        
#======================= Logo & Title ===========================
        self.photo = PhotoImage(file="icon2.png")
        self.label = Label(image=self.photo)
        self.label.grid(row=0, column=0)
        
        self.label = Label(text="Student Portal", font=('arial', 20, 'bold'), fg='dark blue')
        self.label.grid(row=8, column=0)

#======================== New Record ============================
        frame = LabelFrame(self.root, text="Add New Record")
        frame.grid(row=0, column=1, padx=8, pady=8)

        Label(frame, text="Firstname:").grid(row=1, column=1, sticky=W)
        self.firstname = Entry(frame)
        self.firstname.grid(row=1, column=2)

        Label(frame, text="Lastname:").grid(row=2, column=1, sticky=W)
        self.lastname = Entry(frame)
        self.lastname.grid(row=2, column=2)

        Label(frame, text="Username:").grid(row=3, column=1, sticky=W)
        self.username = Entry(frame)
        self.username.grid(row=3, column=2)

        Label(frame, text="Email:").grid(row=4, column=1, sticky=W)
        self.email = Entry(frame)
        self.email.grid(row=4, column=2)


        Label(frame, text="Subject:").grid(row=5, column=1, sticky=W)
        self.subject = Entry(frame)
        self.subject.grid(row=5, column=2)

        Label(frame, text="Age:").grid(row=6, column=1, sticky=W)
        self.age = Entry(frame)
        self.age.grid(row=6, column=2)

       #================ Add Button ========================
        ttk.Button(frame, text="Add Record", command=self.add).grid(row=7, column=2)  
      
      #======================= Message Display ========================
        self.message = Label(text="", fg="red")
        self.message.grid(row=8, column=1)

        #======================= Table Display ========================
        self.tree = ttk.Treeview(height=10, columns=["", "", "", "", "", ""])
        self.tree.grid(row=9, column=0, columnspan=2)

        self.tree.heading("#0", text="ID")
        self.tree.column("#0", width=50)

        self.tree.heading("#1", text="Firstname")
        self.tree.column("#1", width=80)

        self.tree.heading("#2", text="Lastname")
        self.tree.column("#2", width=80)

        self.tree.heading("#3", text="Username")
        self.tree.column("#3", width=80)

        self.tree.heading("#4", text="Email")
        self.tree.column("#4", width=120)

        self.tree.heading("#5", text="Subject")
        self.tree.column("#5", width=80)

        self.tree.heading("#6", text="Age")
        self.tree.column("#6", width=40, stretch=FALSE)

#======================= Time and Date ===========================

        def tick():
            d = datetime.datetime.now()
            today = "{:%B %d, %Y}".format(d)

            time2 = time.strftime('%I:%M:%S %p')
            self.lblInfo.config(text= time2+'\t'+today)
            self.lblInfo.after(200, tick)
        
        self.lblInfo = Label(font=('arial', 20, 'bold'), fg='dark blue')
        self.lblInfo.grid(row=10, column=0, columnspan=2)
        tick()

#======================= Menu Bar ===========================
        chooser = Menu(root)
        root.config(menu=chooser)
        itemone = Menu()

        itemone.add_command(label="Add Record", command=self.add)
        itemone.add_command(label="Edit Record", command = self.edit)
        itemone.add_command(label="Delete Record", command=self.dele)
        itemone.add_separator()
        itemone.add_command(label="Export Data", command=self.export_data)  # Export option
        itemone.add_command(label="Print Data", command=self.print_data)    # Print option
        itemone.add_separator()
        itemone.add_command(label="Help", command = self.help)
        itemone.add_command(label="Exit", command = self.ex)

        chooser.add_cascade(label="File", menu=itemone)
        chooser.add_cascade(label="Add", command=self.add)
        chooser.add_cascade(label="Edit", command = self.edit)
        chooser.add_cascade(label="Delete", command=self.dele)
        chooser.add_cascade(label="Help", command = self.help)
        chooser.add_cascade(label="Exit", command = self.ex)

        self.view_records()

#=======================  View Database Table ===========================
    def run_query(self, query, parameters=()):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result

    def view_records(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        query = "SELECT * FROM studentlist"
        db_table = self.run_query(query)
        for data in db_table:
            self.tree.insert("",1000, text=data[0], values=(data[1:]))
 
   #=======================  Add New  Record ===========================
    def validation(self):
        return len(self.firstname.get()) != 0 and len(self.lastname.get()) != 0 and len(self.username.get()) != 0 and len(self.email.get()) != 0 and len(self.subject.get()) != 0 and len(self.age.get()) != 0

    def add_record(self):
        if self.validation():
            query = "INSERT INTO studentlist VALUES(NULL, ?, ?, ?, ?, ?, ?)"
            parameters = (self.firstname.get(), self.lastname.get(), self.username.get(), self.email.get(), self.subject.get(), self.age.get())
            self.run_query(query, parameters)
            self.message["text"] = "Record {} {} is added".format(self.firstname.get(), self.lastname.get())

            #=================================== Clear fields ===================================
            self.firstname.delete(0, END)
            self.lastname.delete(0, END)
            self.username.delete(0, END)
            self.email.delete(0, END)
            self.subject.delete(0, END)
            self.age.delete(0, END)
        else:
            self.message["text"] = "Fields are required"
        self.view_records()

    def add(self):
        ad = messagebox.askquestion("Add Record", "D you want to add a record?")
        if ad == "yes":
            self.add_record()
        
   
    def delete_record(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["values"][1]
        
        except IndexError as e:
            self.message["text"] = "Please select a record"
            return

        self.message["text"] = ""
        number = self.tree.item(self.tree.selection())["text"]
        query = "DELETE FROM studentlist WHERE id = ?"
        self.run_query(query, (number, ))
        self.message["text"] = "Record {} deleted".format(number)

        self.view_records()

    def dele(self):
        de = messagebox.askquestion("Delete Record", "Do you want to delete a record?")
        if de == "yes":
            self.delete_record()


     #=======================  Edit Record ===========================
    def edit_box(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["values"][0]
        
        except IndexError as e:
            self.message["text"] = "Please select a record to edit"
            return

        fname = self.tree.item(self.tree.selection())["values"][0]
        lname = self.tree.item(self.tree.selection())["values"][1]
        uname = self.tree.item(self.tree.selection())["values"][2]
        mail = self.tree.item(self.tree.selection())["values"][3]
        sub = self.tree.item(self.tree.selection())["values"][4]
        age = self.tree.item(self.tree.selection())["values"][5]

        self.edit_wind = Toplevel()
        self.edit_wind.title = "Edit Record"

        #======================= Old Data / New Data ===========================
        Label(self.edit_wind, text="Old Firstname:").grid(row=0, column=1, sticky=W)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=fname), state="readonly").grid(row=0, column=2)

        new_fname = Label(self.edit_wind, text="New Firstname:").grid(row=1, column=1)
        new_fname = Entry(self.edit_wind)
        new_fname.grid(row=1, column=2)


        Label(self.edit_wind, text="Old Lastname:").grid(row=2, column=1, sticky=W)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=lname), state="readonly").grid(row=2, column=2)

        new_lname = Label(self.edit_wind, text="New Lastname:").grid(row=3, column=1)
        new_lname = Entry(self.edit_wind)
        new_lname.grid(row=3, column=2)

        Label(self.edit_wind, text="Old Username:").grid(row=4, column=1, sticky=W)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=uname), state="readonly").grid(row=4, column=2)

        new_uname = Label(self.edit_wind, text="New Username:").grid(row=5, column=1)
        new_uname = Entry(self.edit_wind)
        new_uname.grid(row=5, column=2)

        Label(self.edit_wind, text="Old Email:").grid(row=6, column=1, sticky=W)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=mail), state="readonly").grid(row=6, column=2)

        new_mail = Label(self.edit_wind, text="New Email:").grid(row=7, column=1)
        new_mail = Entry(self.edit_wind)
        new_mail.grid(row=7, column=2)


        Label(self.edit_wind, text="Old Subject:").grid(row=8, column=1, sticky=W)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=sub), state="readonly").grid(row=8, column=2)

        new_sub = Label(self.edit_wind, text="New Subject:").grid(row=9, column=1)
        new_sub = Entry(self.edit_wind)
        new_sub.grid(row=9, column=2)

        Label(self.edit_wind, text="Old Age:").grid(row=10, column=1, sticky=W)
        Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=age), state="readonly").grid(row=10, column=2)

        new_age = Label(self.edit_wind, text="New Age:").grid(row=11, column=1)  
        new_age = Entry(self.edit_wind)
        new_age.grid(row=11, column=2)

        
        Button(self.edit_wind, text="Save Changes", command=lambda: self.edit_record(new_fname.get(),
                                        fname, new_lname.get(), lname, new_uname.get(), uname, new_mail.get(), mail, new_sub.get(), sub,
                                        new_age.get(), age)).grid(row=12, column=2, sticky=W)

        
        self.edit_wind.mainloop()

    
    def edit_record(self, new_fname, fname, new_lname, lname, new_uname, uname, new_mail, mail, new_sub, sub, new_age, age):
        query = "UPDATE studentlist SET Firstname =?, Lastname =?, Username =?, Email=?, Subject=?, Age=? WHERE Firstname =? AND Lastname =? AND Username =? AND Email=? AND Subject=? AND Age=?"
        parameters = (new_fname, new_lname, new_uname, new_mail, new_sub, new_age, fname, lname, uname, mail, sub, age)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message["text"] = "{} details were changed to {}".format(fname, new_fname)
        self.view_records()
    
    def edit(self):
        ed = messagebox.askquestion("Edit Record", "Do you want to Edit a record?")
        if ed == "yes":
            self.edit_box()
    
    
    def help(self):
        messagebox.showinfo("Log", "Report sent")

    def ex(self): 
        exi = messagebox.askquestion("Exit Application", "Do you want to Close application?")
        if exi == "yes":
            root.destroy()


    # Function to export data to a CSV file
    def export_data(self):
        try:
            # Ask the user where to save the file
            file_path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not file_path:
                return  # User canceled the save dialog

            # Fetch data from the database
            query = "SELECT * FROM studentlist"
            records = self.run_query(query)

            # Write data to the CSV file
            with open(file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Firstname", "Lastname", "Username", "Email", "Subject", "Age"])  # Header row
                for record in records:
                    writer.writerow(record)

            messagebox.showinfo("Export Successful", f"Data exported successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred: {e}")

     # Function to print data
    def print_data(self):
        try:
            # Fetch data from the database
            query = "SELECT * FROM studentlist"
            records = self.run_query(query)

            # Create a temporary text file for printing
            temp_file = "temp_print.txt"
            with open(temp_file, mode="w") as file:
                file.write("Student Records\n")
                file.write("=" * 50 + "\n")
                file.write(f"{'ID':<5}{'Firstname':<15}{'Lastname':<15}{'Username':<15}{'Email':<25}{'Subject':<15}{'Age':<5}\n")
                file.write("=" * 50 + "\n")
                for record in records:
                    file.write(f"{record[0]:<5}{record[1]:<15}{record[2]:<15}{record[3]:<15}{record[4]:<25}{record[5]:<15}{record[6]:<5}\n")

            # Open the print dialog
            os.startfile(temp_file, "print")
        except Exception as e:
            messagebox.showerror("Print Failed", f"An error occurred: {e}")


        # Add this at the end of your __init__ method, after all other widgets
        self.footer = Label(
            self.root,
            text="© 2025 Juaboso Senior High School | All Rights Reserved",
            bg="navy",         # Footer background color
            fg="white",        # Footer text color
            font=('Arial', 10, 'italic')
        )
        self.footer.grid(row=10, column=0, columnspan=3, sticky="we")  # Adjust row/columnspan as needed

if __name__ == "__main__":
    root = Tk()
    root.geometry("530x490+500+200")
    application = School_Portal(root)
    root.mainloop()