from common import *
import PRB
from MappingFunction import mappingFunction
import time
import csv

rows = [[sampleSize] for sampleSize in range(30, 101, 5)]

class ProbabilityVerificationServer():
	def __init__(self) -> None:
		pass

	def setup(self, degree = 3, randomCoeff = False):
		self.fc = FunctionalCommitment(degree, randomCoeff)
		c = self.fc.getCommitment()

		# write PK, c, M, n onto bulletin board
		with open(BulletinBoardDir + CommitmentFileName, 'w') as f:
			f.write(serializeECC(c))
            
	def eval(self):
		seed = PRB.eval()
		testData = mappingFunction.mapToTestData(seed)

		result = []
		start = time.time()
		i = 0
		row = 0
		for r, o in testData:
			i += 1
			input = LootBoxInput(r, o)
			y, W = self.fc.evalAndProof(input)
			if i >= 30 and i % 5 == 0:
				rows[row].append(time.time() - start)
				row += 1

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
	testData = mappingFunction.mapToTestData(seed)

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
	row = 0
	start = time.time()
	for i in range(len(testData)):
		r, o = testData[i]
		input = LootBoxInput(r, o)
		y, W = evalProofs[i]
		if not verifyEvalProof(c, input, y, W):
			print(f"Verification failed on {i}th input, input: {input}, y: {y}, W: {W}")
			return False
		if isWinning(y):
			winningNumber += 1

		if i+1 >= 30 and (i+1) % 5 == 0:
			rows[row].append(time.time() - start)
			row += 1
		
	print(f"Verification done, amount: {len(testData)}, #winning: {winningNumber}, sample winning probability: {winningNumber / len(testData)}")
	return True

def sampleRun():
	server = ProbabilityVerificationServer()
	server.setup()
	server.eval()
	verifyProbability()

def plotDifferentDegree():
	server = ProbabilityVerificationServer()
	rows = [["degree", "setup", "evaluation", "verification"]]
	for degree in range(100, 201, 10):
		t1 = time.time()
		server.setup(degree, True)
		t2 = time.time()
		server.eval()
		t3 = time.time()
		verifyProbability()
		t4 = time.time()

		rows.append([degree, t2-t1, t3-t2, t4-t3])

	with open("experiment/pv_degree_100_200.csv", 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(rows)

def plotDifferentSampleSize():
	server = ProbabilityVerificationServer()
	rows = [["Sample Size", "evaluation", "verification"]]
	server.setup(150, True)
	for sampleSize in range(30, 101, 10):
		mappingFunction.setSampleSize(sampleSize)
		t2 = time.time()
		server.eval()
		t3 = time.time()
		verifyProbability()
		t4 = time.time()

		rows.append([sampleSize, t3-t2, t4-t3])

	with open("experiment/pv_sample_size_30_100.csv", 'w', newline='') as f:
		writer = csv.writer(f)
		writer.writerows(rows)

if __name__ == "__main__":
	# server = ProbabilityVerificationServer()
	# server.setup(3, True)
	# server.eval()
	# verifyProbability()
	# print(rows)
	sampleRun()
	# plotDifferentDegree()
	# plotDifferentSampleSize()

	

