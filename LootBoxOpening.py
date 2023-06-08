from common import *
from MappingFunction import mappingFunction

class LootBoxOpeningServer():
	def __init__(self) -> None:
		pass
    
	def setup(self):
		self.fc = FunctionalCommitment(3)
		self.chain = ["random_seed"]
		for _ in range(100):
			previousElement = self.chain[-1]
			new_hash = hashlib.sha256(previousElement.encode()).hexdigest()
			self.chain.append(new_hash)

		self.current = len(self.chain) - 1
		return self.chain[-1]
	
	def eval(self, beta, o):
		# first verify the validity of beta and o

		self.current -= 1
		if self.current == 0:
			print("Please re-run the setup to update the hash chain")
			return None
		previousElement = self.chain[self.current]
		r = previousElement + beta
		y, W = self.fc.evalAndProof(LootBoxInput(r, o))
		return (previousElement, y, W)
	
class LootBoxOpeningClient():
	def __init__(self, lastElement, server) -> None:
		self.current = lastElement
		self.server = server

	def requestOpening(self):
		beta = mappingFunction.generate_random_string(10)
		o = mappingFunction.generate_random_string(10)

		# call eval of the server
		previousElement, y, W = server.eval(beta, o)

		# 1. verify hash
		if hashlib.sha256(previousElement.encode()).hexdigest() != self.current:
			print(f"Failed to verify the hash chain element, H({previousElement}) != {self.current}")
			return None
		
		# 2. verify the evaluation proof of FC
		with open(BulletinBoardDir + CommitmentFileName, 'r') as f:
			c = deserializeEcc(f.read())
		input = LootBoxInput(previousElement + beta, o)
		if not verifyEvalProof(c, input, y, W):
			print(f"Failed to verify the evaluation proof, input: {input}, y: {y}, W: {W}")
			return None

		# 3. update current
		self.current = previousElement

		if isWinning(y):
			print("Opening succeeded, you won the loot box!!!")
		else:
			print("Opening succeeded, you didn't win the loot box QAQ")
	
if __name__ == "__main__":
	server = LootBoxOpeningServer()
	lastElement = server.setup()
	client = LootBoxOpeningClient(lastElement, server)
	for _ in range(10):
		client.requestOpening()
