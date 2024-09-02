import os
import re
import subprocess

PROTO_FILE = 'machine.proto'  
SERVER_FILE = 'server.py'
BLOB_FILE = "machines_blob.pkl"
PROTO_PATH = '.' 

# identify GetMachineBy methods and machine fields
GET_METHOD_PATTERN = r'rpc GetMachineBy([A-Za-z]+)\('
FIELD_PATTERN = r'string ([a-zA-Z_]+) ='

def parse_proto(proto_file):
    methods = []
    fields = []
    with open(proto_file, 'r') as file:
        content = file.read()
        methods = re.findall(GET_METHOD_PATTERN, content)
        fields = re.findall(FIELD_PATTERN, content)
    return methods, fields

def regenerate_grpc_stubs():
    print("Regenerating gRPC stubs...")
    command = [
        'python3', '-m', 'grpc_tools.protoc',
        '-I.',  # Include current directory for imports
        f'--python_out={PROTO_PATH}',
        f'--grpc_python_out={PROTO_PATH}',
        PROTO_FILE
    ]
    subprocess.run(command, check=True)

def generate_server_code(methods, fields):
    code = f"""import grpc
from concurrent import futures
import machine_pb2
import machine_pb2_grpc
import pickle
import os

BLOB_FILE = "{BLOB_FILE}"

class MachineService(machine_pb2_grpc.MachineServiceServicer):
    def __init__(self):
        self.machines = []
        if os.path.exists(BLOB_FILE):
            with open(BLOB_FILE, 'rb') as f:
                self.machines = pickle.load(f)

    def save_to_blob(self):
        with open(BLOB_FILE, 'wb') as f:
            pickle.dump(self.machines, f)
    """

    for method in methods:
        code += f"""
    def GetMachineBy{method}(self, request, context):
        matched_machines = [machine for machine in self.machines if machine.{method.lower()} == request.{method.lower()}]
        return machine_pb2.MachineList(machines=matched_machines)
    """


    code += """
    def UpdateMachine(self, request, context):
        for machine in self.machines:
            if machine.id == request.id:
    """

    for field in fields:
        code += f"""
                if request.{field}:
                    machine.{field} = request.{field}
        """
    
    code += """
                self.save_to_blob()
                return machine_pb2.UpdateMachineResponse(message="Machine updated successfully.")
        return machine_pb2.UpdateMachineResponse(message="Machine not found.")
    """

    # Add any additional custom methods here
    code += """
    def GetAllMachines(self, request, context):
        return machine_pb2.MachineList(machines=self.machines)
    """

    code += """
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    machine_pb2_grpc.add_MachineServiceServicer_to_server(MachineService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
    """
    return code

def update_server_file():
    methods, fields = parse_proto(PROTO_FILE)
    server_code = generate_server_code(methods, fields)
    with open(SERVER_FILE, 'w') as file:
        file.write(server_code)

def main():
    regenerate_grpc_stubs()
    update_server_file()

if __name__ == '__main__':
    main()

