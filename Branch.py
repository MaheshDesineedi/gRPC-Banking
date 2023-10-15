from concurrent import futures
import json
import sys

import grpc
import bank_pb2
import bank_pb2_grpc


class Branch(bank_pb2_grpc.BankServicer):

    def __init__(self, id, balance, branches):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches
        for branch in self.branches:
            channel = grpc.insecure_channel(f"localhost:{branch}")
            stub = bank_pb2_grpc.BankStub(channel)
            self.stubList.append(stub)

    # Helper method. Not an RPC method
    def propogate(self, interface, money):
        for stub in self.stubList:
            response = stub.MsgDelivery(bank_pb2.BankRequest(interface=interface, money=money))

            if(response.result == "failed"):
                print(f"{interface} failed from Branch ID: {self.id}")

    # RPC method to handle Customer and Branch requests
    def MsgDelivery(self, request, context):

        if request.interface == "query":
            return bank_pb2.BankResponse(result="success", balance=self.balance)
        elif request.interface == "deposit":
            self.balance = self.balance + request.money

            # propogate deposit
            for stub in self.stubList:
                response = stub.MsgDelivery(bank_pb2.BankRequest(interface="Propogate_Deposit", money=request.money))

                if(response.result == "failed"):
                    return bank_pb2.BankResponse(result="failed", balance=self.balance)

            return bank_pb2.BankResponse(result="success", balance=self.balance)
        elif request.interface == "withdraw":
            self.balance = self.balance - request.money

            # propogate withdraw
            for stub in self.stubList:
                response = stub.MsgDelivery(bank_pb2.BankRequest(interface="Propogate_Withdraw", money=request.money))

                if(response.result == "failed"):
                    return bank_pb2.BankResponse(result="failed", balance=self.balance)

            return bank_pb2.BankResponse(result="success", balance=self.balance)
        elif request.interface == "Propogate_Deposit":
            self.balance = self.balance + request.money
            return bank_pb2.BankResponse(result="success", balance=self.balance)
        elif request.interface == "Propogate_Withdraw":
            self.balance = self.balance - request.money
            return bank_pb2.BankResponse(result="success", balance=self.balance)


def serve(id, balance, branches):
    port = 50050 + id  # add the offset for the branch port
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    bank_pb2_grpc.add_BankServicer_to_server(Branch(id, balance, branches), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server started. Listening on port {port}")
    server.wait_for_termination()


# parse arguments
parameters = json.loads(str(sys.argv[1]).replace("\'", "\""))

serve(int(parameters["id"]), int(parameters["balance"]), parameters["branches"])
