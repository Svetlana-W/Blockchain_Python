# Create a Cryptocurrency

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4               # Generate unique random address
from urllib.parse import urlparse

# Transforming a general purpose blockchain inte cryptocurrency:
# 1 -1)Adding transactions into the Blockchain class
#    2)Building a concensus function (to make sure that each node in the decentralised network has the same chain)
# Introducing a separate list which contains transactions before they are added to the block (transactions are appened to that list, and then all accumulate transactions are added to the block when the block is mined)


class Blockchain:        # Defining the class
    
    def __init__(self):  # Initialising init method with the 'self' argument which referes to the object which created when the clsss is made
        self.chain = []  # Initialising chain itself (list, containing blocks)
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')  # Genesis block
        self.nodes = set() #Initialisin an empty set (the nodes in the web are unordered, so it can't be a list)
        
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        self.transactions = [] # Emptying the transactions list after the original transactions were added to the block
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    # Check if each block has a coorrect proof_of_work, and that the previous hash of each block is equal to the hash of previous block, hence I have a valid blockchain
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
        
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
# Replacing any chain that is shorter than the longest chain among all the nodes of the network
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True          # Specifying that the chain was replaced
        return False             # The chain was not replaced as it originally was the longest one
    
        
# 2 - Mining a blockchain (two functions: to display a blockchain and to mine a new block)
# Integrating a transactions
# Creating more nodes

# Creating a Web App
app = Flask(__name__) # Creating an instance of Flask class
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')  # Removing dashes


# Creating a Blockchain
blockchain = Blockchain()   # Creating an instance object of Blockchain
# Mining a new block

@app.route('/mine_block', methods = ['GET']) # route() decorator tells Flask what URL should be trigger for the function
                                        # specifying which URL will trigger function
def mine_block():
    # get a proof
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Sviet', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!', 
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']}
    return jsonify(response), 200

# Getting the full Blockchain and displaying it
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}

    return jsonify(response), 200

# Checking if blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    valid = blockchain.is_chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'Evrething is great. Blockchain is valid.'}
    else:
        response = {'message': 'Something is not right. The Blockchain is not vaid.'}
    return jsonify(response), 200

#Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])

def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing. Check sender, receiver and amount.', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201


# 3 - Decentralising Blockchain  

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])

def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Svicoin Blockchain now contains the following nodes: ',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain in any node that is not up to date on the blockchain (does not containg the last version of the blockchain)
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes have different chains so the chain was replaced by the longest one.' ,
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the longest one.' ,
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200



# Running the app
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
    
  
    