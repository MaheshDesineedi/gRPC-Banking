import grpc

import bank_pb2
import bank_pb2_grpc

class Customer:
    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = None


    def createStub(self):
        port = 50050 + int(self.id)  # add the offset for the branch port
        channel = grpc.insecure_channel(f"localhost:{port}")
        self.stub = bank_pb2_grpc.BankStub(channel)


    def executeEvents(self):
        bank_responses = []

        for event in self.events:
            response = dict()

            if event["interface"] == "query":
                bank_response = self.stub.MsgDelivery(bank_pb2.BankRequest(interface="query"))
                response["interface"] = event["interface"]
                response["balance"] = bank_response.balance
                bank_responses.append(response)

            elif event["interface"] == "deposit":
                bank_response = self.stub.MsgDelivery(bank_pb2.BankRequest(interface="deposit", money=event["money"]))
                response["interface"] = event["interface"]
                response["result"] = bank_response.result
                bank_responses.append(response)

            elif event["interface"] == "withdraw":
                    bank_response = self.stub.MsgDelivery(bank_pb2.BankRequest(interface="withdraw", money=event["money"]))
                    response["interface"] = event["interface"]
                    response["result"] = bank_response.result
                    bank_responses.append(response)


        return bank_responses
