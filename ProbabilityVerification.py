from common import *
import PRB
import MappingFunction

class ProbabilityVerificationServer():
	def __init__(self) -> None:
		pass

	def setup(self):
		self.fc = FunctionalCommitment(3)
		c = self.fc.getCommitment()

		# write PK, c, M, n onto bulletin board
		with open(BulletinBoardDir + CommitmentFileName, 'w') as f:
			f.write(serializeECC(c))
            
	def eval(self):
		seed = PRB.eval()
		testData = MappingFunction.mapToTestData(seed)

		result = []
		for r, o in testData:
			input = LootBoxInput(r, o)
			y, W = self.fc.evalAndProof(input)
			result.append((y, W))

		print(W, type(W), type(W[0]))
		print("Evaluation succeeded, write the evaluation and proofs on the bulletin board.")
		with open(BulletinBoardDir + EvalProofFileName, 'w') as f:
			for y, W in result:
				f.write(str(y.v) + "#" + serializeECC(W))
				f.write('\n')

def verifyProbability() -> bool:
	# get commitment c from bulletin board
	with open(BulletinBoardDir + CommitmentFileName, 'r') as f:
		s = f.read()
		c = deserializeEcc(s)

	seed = PRB.eval()
	testData = MappingFunction.mapToTestData(seed)

	# get eval proofs from bulletin board
	evalProofs = []
	with open(BulletinBoardDir + EvalProofFileName, 'r') as f:
		for line in f.readlines():
			a, b = line.strip().split("#")
			y = F(int(a))
			W = deserializeEcc(b)
			evalProofs.append((y ,W))

	if len(testData) != len(evalProofs):
		print(f"Inconsistent amount: testData {len(testData)}, evalProofs {len(evalProofs)}")
		return False

	# verify eval proofs
	winningNumber = 0
	for i in range(len(testData)):
		r, o = testData[i]
		input = LootBoxInput(r, o)
		y, W = evalProofs[i]
		if not verifyEvalProof(c, input, y, W):
			print(f"Verification failed on {i}th input, input: {input}, y: {y}, W: {W}")
			return False
		if isWinning(y):
			winningNumber += 1
		
	print(f"Verification done, amount: {len(testData)}, #winning: {winningNumber}, sample winning probability: {winningNumber / len(testData)}")
	return True

if __name__ == "__main__":
	server = ProbabilityVerificationServer()
	server.setup()
	server.eval()
	verifyProbability()

