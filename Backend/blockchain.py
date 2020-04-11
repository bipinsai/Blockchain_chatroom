import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests
import random

class Blockchain:

    def __init__(self):
        self.chain = []
        self.data = ""
        self.createBlock(nonce = 1, previous_hash = '0')
        self.nodes = set()
        self.storage = {'sender':'',
                        'msg':'',
                        'h':'',
                        's':''}
    
    def createBlock(self, nonce, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': nonce,
                 'previous_hash': previous_hash,
                 'data': self.data}
        self.data = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce
    
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
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_data(self, sender='', msg='', param='', param_type=''):
        if msg=='mining_block':
            if len(self.data)==0: return -1
            else: return -2
        if param_type=='h':
            self.storage['sender'] = sender
            self.storage['msg'] = msg
            self.storage['h'] = param
            self.storage['b'] = random.randint(0, 1)
            return self.storage['b']
        elif param_type=='s':
            self.storage['s'] = param
            keys = self.get_publickeys(self.storage['sender'])
            if self.verifyTransaction(keys["A"], keys["B"], keys["p"]):
                self.data.append({'sender': self.storage['sender'],
                                    'time': str(datetime.datetime.now()),
                                    # 'time': self.storage['time'],
                                    'msg': self.storage['msg']})
                previous_block = self.get_previous_block()
                return previous_block['index'] + 1
        return -99
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
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
            return True
        return False

    def get_publickeys(self, user):
        with open('publickeys.json') as f:
            keys = json.load(f)
        return keys[user]

    def verifyTransaction(self, A, B, p):
        s = self.storage['s']
        h = self.storage['h']
        b = self.storage['b']

        if (A**s)%p == (h*B**b)%p:
            return True
        else:
            return False