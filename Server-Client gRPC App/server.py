import grpc
from concurrent import futures
import machine_pb2
import machine_pb2_grpc
import pickle
import os

BLOB_FILE = "machines_blob.pkl"

class MachineService(machine_pb2_grpc.MachineServiceServicer):
    def __init__(self):
        self.machines = []
        if os.path.exists(BLOB_FILE):
            with open(BLOB_FILE, 'rb') as f:
                self.machines = pickle.load(f)

    def save_to_blob(self):
        with open(BLOB_FILE, 'wb') as f:
            pickle.dump(self.machines, f)
    
    def GetMachineById(self, request, context):
        matched_machines = [machine for machine in self.machines if machine.id == request.id]
        return machine_pb2.MachineList(machines=matched_machines)
    
    def GetMachineByName(self, request, context):
        matched_machines = [machine for machine in self.machines if machine.name == request.name]
        return machine_pb2.MachineList(machines=matched_machines)
    
    def GetMachineByCfg(self, request, context):
        matched_machines = [machine for machine in self.machines if machine.cfg == request.cfg]
        return machine_pb2.MachineList(machines=matched_machines)
    
    def GetMachineByAdr(self, request, context):
        matched_machines = [machine for machine in self.machines if machine.adr == request.adr]
        return machine_pb2.MachineList(machines=matched_machines)
    
    def UpdateMachine(self, request, context):
        for machine in self.machines:
            if machine.id == request.id:
    
                if request.id:
                    machine.id = request.id
        
                if request.name:
                    machine.name = request.name
        
                if request.cfg:
                    machine.cfg = request.cfg
        
                if request.id:
                    machine.id = request.id
        
                if request.name:
                    machine.name = request.name
        
                if request.cfg:
                    machine.cfg = request.cfg
        
                if request.adr:
                    machine.adr = request.adr
        
                if request.message:
                    machine.message = request.message
        
                self.save_to_blob()
                return machine_pb2.UpdateMachineResponse(message="Machine updated successfully.")
        return machine_pb2.UpdateMachineResponse(message="Machine not found.")
    
    def GetAllMachines(self, request, context):
        return machine_pb2.MachineList(machines=self.machines)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    machine_pb2_grpc.add_MachineServiceServicer_to_server(MachineService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
    