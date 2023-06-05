from flask import Flask
import hashlib
from KZG10 import *
import time
from py_ecc import fields


# Global variables
F = GF(curve.curve_order)
PK = TrustedSetup.generate(F, 10, True)
intervals = 10
CommonPolynomial = [8,7,8,6,5,3,2,1,2,3,4,5,7]
BulletinBoardDir = "./BulletinBoard/"
CommitmentFileName = "commitment.txt"
EvalProofFileName = "evaluation_proofs.txt"

class LootBoxInput():
	def __init__(self, r, o):
		self.r = r
		self.o = o

	def getFieldInput(self):
		string_input = self.r + self.o
		hashed_value = hashlib.sha256(string_input.encode()).hexdigest()
		return F(int(hashed_value, 16))


class FunctionalCommitment():
	def __init__(self, degree = 3) -> None:
		self.degree = degree
		self.coeff = [F(CommonPolynomial[i]) for i in range(degree)]
		self.c = CommitSum(PK, self.coeff)

	def getCommitment(self):
		return self.c
    
	def evalAndProof(self, input: LootBoxInput):
		i = input.getFieldInput()
		print(f"Eval on input {i}")

		y = polynomial(i, self.coeff)
		W = CommitDivision(PK, i, self.coeff)
		
		return y, W
	
def verifyEvalProof(c, input: LootBoxInput, y, W) -> bool:
	i = input.getFieldInput()
	print(f"Verify on input {i}, output {y}, witness {W}, commitment {c}")

	g2_i = curve.multiply(curve.G2, int(i))
	g2_x_sub_i = curve.add(PK.g2_powers[1], curve.neg(g2_i)) # x-i
	g1_phi_at_i = curve.multiply(curve.G1, int(y))
	g1_phi_at_x_sub_i = curve.add(c, curve.neg(g1_phi_at_i))
	a = curve.pairing(g2_x_sub_i, W)
	b = curve.pairing(curve.G2, curve.neg(g1_phi_at_x_sub_i))
	ab = a*b
	print('ab', ab)
	return ab == curve.FQ12.one()

if __name__ == "__main__":
	fc = FunctionalCommitment()
	c = fc.getCommitment()

	with open("BulletinBoard.txt", "w") as f:
		f.write(str(c[0]))
		f.write("###")
		f.write(str(c[1]))

	with open("BulletinBoard.txt", "r") as f:
		s = f.read().split("###")
		a = (curve.FQ(int(s[0])), curve.FQ(int(s[1])))
		print(a == c)


def serializeECC(p: Tuple):
	s = str(p[0])
	s += ","
	s += str(p[1])
	return ",".join([str(e) for e in p])

def deserializeEcc(s: str):
	return tuple([curve.FQ(int(e)) for e in s.split(",")])
