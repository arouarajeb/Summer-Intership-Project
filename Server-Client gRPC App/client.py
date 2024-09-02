import tkinter as tk
from tkinter import ttk
import grpc
import machine_pb2
import machine_pb2_grpc

class MachineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Machine Management")
        self.geometry("600x400")

        # Set up gRPC channel and stub
        self.channel = grpc.insecure_channel('localhost:50051')
        self.stub = machine_pb2_grpc.MachineServiceStub(self.channel)

        self.show_main_menu()

    def show_main_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Choose an option", font=("Arial", 16))
        label.pack(pady=20)

        view_all_button = tk.Button(self, text="View All Machines", command=self.view_all_machines)
        view_all_button.pack(pady=10)

        """search_button = tk.Button(self, text="Search for a Machine", command=self.show_search_menu)
        search_button.pack(pady=10)"""

        update_button = tk.Button(self, text="Update a Machine", command=self.show_update_menu)
        update_button.pack(pady=10)

        exit_button = tk.Button(self, text="Exit", command=self.quit)
        exit_button.pack(pady=10)

    def view_all_machines(self):
        for widget in self.winfo_children():
            widget.destroy()

        machines = self.stub.GetAllMachines(machine_pb2.Empty()).machines
        columns = ('ID', 'Name', 'CFG')

        tree = ttk.Treeview(self, columns=columns, show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('CFG', text='CFG')

        for machine in machines:
            tree.insert('', tk.END, values=(machine.id, machine.name, machine.cfg))

        tree.pack(expand=True, fill='both')

        back_button = tk.Button(self, text="Back to Main Menu", command=self.show_main_menu)
        back_button.pack(pady=10)

    def show_search_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Search Machine by:", font=("Arial", 16))
        label.pack(pady=20)

        search_id_button = tk.Button(self, text="ID", command=lambda: self.search_machine('id'))
        search_id_button.pack(pady=10)

        search_name_button = tk.Button(self, text="Name", command=lambda: self.search_machine('name'))
        search_name_button.pack(pady=10)

        search_cfg_button = tk.Button(self, text="CFG", command=lambda: self.search_machine('cfg'))
        search_cfg_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Main Menu", command=self.show_main_menu)
        back_button.pack(pady=10)

    def search_machine(self, search_type):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text=f"Enter {search_type.capitalize()}:")
        label.pack(pady=20)

        entry = tk.Entry(self)
        entry.pack(pady=10)

        search_button = tk.Button(self, text="Search", command=lambda: self.perform_search(search_type, entry.get()))
        search_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Search Menu", command=self.show_search_menu)
        back_button.pack(pady=10)

    def perform_search(self, search_type, value):
        if search_type == 'id':
            machine = self.stub.GetMachineById(machine_pb2.MachineIdRequest(id=value))
            machines = [machine] if machine.id else []
        elif search_type == 'name':
            machines = self.stub.GetMachineByName(machine_pb2.MachineNameRequest(name=value)).machines
        elif search_type == 'cfg':
            machines = self.stub.GetMachineByCfg(machine_pb2.MachineCfgRequest(cfg=value)).machines

        self.display_machines(machines)

    def show_update_menu(self):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Update Machine by:", font=("Arial", 16))
        label.pack(pady=20)

        update_id_button = tk.Button(self, text="ID", command=lambda: self.update_machine_search('id'))
        update_id_button.pack(pady=10)

        update_name_button = tk.Button(self, text="Name", command=lambda: self.update_machine_search('name'))
        update_name_button.pack(pady=10)

        update_cfg_button = tk.Button(self, text="CFG", command=lambda: self.update_machine_search('cfg'))
        update_cfg_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Main Menu", command=self.show_main_menu)
        back_button.pack(pady=10)

    def update_machine_search(self, search_type):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text=f"Enter {search_type.capitalize()}:")
        label.pack(pady=20)

        entry = tk.Entry(self)
        entry.pack(pady=10)

        search_button = tk.Button(self, text="Search", command=lambda: self.perform_update_search(search_type, entry.get()))
        search_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Update Menu", command=self.show_update_menu)
        back_button.pack(pady=10)

    def perform_update_search(self, search_type, value):
        if search_type == 'id':
            machine = self.stub.GetMachineById(machine_pb2.MachineIdRequest(id=value))
            machines = [machine] if machine.id else []
        elif search_type == 'name':
            machines = self.stub.GetMachineByName(machine_pb2.MachineNameRequest(name=value)).machines
        elif search_type == 'cfg':
            machines = self.stub.GetMachineByCfg(machine_pb2.MachineCfgRequest(cfg=value)).machines

        if len(machines) == 0:
            tk.messagebox.showinfo("No Results", "No machines found.")
            self.show_update_menu()
        elif len(machines) == 1:
            self.update_single_machine(machines[0])
        else:
            self.update_multiple_machines(machines)

    def update_single_machine(self, machine):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text=f"Update Machine ID: {machine.id}")
        label.pack(pady=20)

        name_label = tk.Label(self, text=f"Current Name: {machine.name}")
        name_label.pack(pady=5)
        name_entry = tk.Entry(self)
        name_entry.insert(0, machine.name)
        name_entry.pack(pady=5)

        cfg_label = tk.Label(self, text=f"Current CFG: {machine.cfg}")
        cfg_label.pack(pady=5)
        cfg_entry = tk.Entry(self)
        cfg_entry.insert(0, machine.cfg)
        cfg_entry.pack(pady=5)

        def update_machine():
            new_name = name_entry.get()
            new_cfg = cfg_entry.get()
            updated_machine = machine_pb2.Machine(id=machine.id, name=new_name, cfg=new_cfg)
            response = self.stub.UpdateMachine(updated_machine)
            tk.messagebox.showinfo("Update Status", response.message)
            self.show_main_menu()

        update_button = tk.Button(self, text="Update", command=update_machine)
        update_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Update Menu", command=self.show_update_menu)
        back_button.pack(pady=10)

    def update_multiple_machines(self, machines):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Multiple Machines Found", font=("Arial", 16))
        label.pack(pady=20)

        columns = ('ID', 'Name', 'CFG')
        tree = ttk.Treeview(self, columns=columns, show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('CFG', text='CFG')

        for machine in machines:
            tree.insert('', tk.END, values=(machine.id, machine.name, machine.cfg))

        tree.pack(expand=True, fill='both')

        update_individually_button = tk.Button(self, text="Update Individually", command=lambda: self.update_each_machine_individually(machines))
        update_individually_button.pack(pady=10)

        update_all_button = tk.Button(self, text="Update CFG for All", command=lambda: self.update_cfg_for_all(machines))
        update_all_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Update Menu", command=self.show_update_menu)
        back_button.pack(pady=10)

    def update_each_machine_individually(self, machines):
        self.current_machine_index = 0
        self.machines_to_update = machines
        self.show_individual_machine_update()

    def show_individual_machine_update(self):
        for widget in self.winfo_children():
            widget.destroy()

        current_machine = self.machines_to_update[self.current_machine_index]

        label = tk.Label(self, text=f"Update Machine ID: {current_machine.id}")
        label.pack(pady=20)

        name_label = tk.Label(self, text=f"Current Name: {current_machine.name}")
        name_label.pack(pady=5)
        name_entry = tk.Entry(self)
        name_entry.insert(0, current_machine.name)
        name_entry.pack(pady=5)

        cfg_label = tk.Label(self, text=f"Current CFG: {current_machine.cfg}")
        cfg_label.pack(pady=5)
        cfg_entry = tk.Entry(self)
        cfg_entry.insert(0, current_machine.cfg)
        cfg_entry.pack(pady=5)

        def update_machine():
            new_name = name_entry.get()
            new_cfg = cfg_entry.get()
            updated_machine = machine_pb2.Machine(id=current_machine.id, name=new_name, cfg=new_cfg)
            response = self.stub.UpdateMachine(updated_machine)
            tk.messagebox.showinfo("Update Status", response.message)

            # Move to the next machine if there is one
            if self.current_machine_index < len(self.machines_to_update) - 1:
                self.current_machine_index += 1
                self.show_individual_machine_update()
            else:
                self.show_update_menu()

        update_button = tk.Button(self, text="Update", command=update_machine)
        update_button.pack(pady=10)

        if self.current_machine_index > 0:
            previous_button = tk.Button(self, text="Previous Machine", command=self.previous_machine)
            previous_button.pack(side=tk.LEFT, padx=10)

        if self.current_machine_index < len(self.machines_to_update) - 1:
            next_button = tk.Button(self, text="Next Machine", command=self.next_machine)
            next_button.pack(side=tk.RIGHT, padx=10)

        back_button = tk.Button(self, text="Back to Update Menu", command=self.show_update_menu)
        back_button.pack(pady=10)

    def next_machine(self):
        if self.current_machine_index < len(self.machines_to_update) - 1:
            self.current_machine_index += 1
            self.show_individual_machine_update()

    def previous_machine(self):
        if self.current_machine_index > 0:
            self.current_machine_index -= 1
            self.show_individual_machine_update()

    def update_cfg_for_all(self, machines):
        for widget in self.winfo_children():
            widget.destroy()

        label = tk.Label(self, text="Update CFG for All Machines", font=("Arial", 16))
        label.pack(pady=20)

        cfg_label = tk.Label(self, text="New CFG:")
        cfg_label.pack(pady=5)
        cfg_entry = tk.Entry(self)
        cfg_entry.pack(pady=5)

        def update_all_machines():
            new_cfg = cfg_entry.get()
            for machine in machines:
                updated_machine = machine_pb2.Machine(id=machine.id, name=machine.name, cfg=new_cfg)
                response = self.stub.UpdateMachine(updated_machine)
            tk.messagebox.showinfo("Update Status", "All machines updated successfully.")
            self.show_main_menu()

        update_button = tk.Button(self, text="Update All", command=update_all_machines)
        update_button.pack(pady=10)

        back_button = tk.Button(self, text="Back to Update Menu", command=self.show_update_menu)
        back_button.pack(pady=10)

if __name__ == "__main__":
    app = MachineApp()
    app.mainloop()
