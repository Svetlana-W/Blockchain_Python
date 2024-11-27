# Module 1 - Create a Blockchain

# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Building a blockchain (the architecture of blockchain)
class Blockchain:        # Defining the class
    
    def __init__(self):  # Initialising init method with the 'self' argument which referes to the object which created when the clsss is made
        self.chain = []  # Initialising chain itself (list, containing blocks)
        self.create_block(proof = 1, previous_hash = '0')  # Genesis block
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
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
        
        
# Mining a blockchain (two functions: to display a blockchain and to mine a new block)

# Creating a Web App
app = Flask(__name__) # Creating an instance of Flask class
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

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
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!', 
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
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

# Running the app
# app.run(host = '0.0.0.0', port = 5000)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)































