from SimulaQron.cqc.pythonLib.cqc import *
import math

class CoinflipConsensus:
    def __init__(self, queue):
        self.queue = queue

    def _atomic_flip(self, candidate1, candidate2, coeff):
        with CQCConnection(candidate1) as Alice:
            qA = qubit(Alice)
            qB = qubit(Alice)
            
            # Bias
            angle = 2 * math.acos(coeff)
            step = int(angle * 256 / (2 * math.pi))
            qA.rot_Y(step)
            qA.cnot(qB)
            qB.X()

            # Send qubit qB to Bob.
            Alice.sendQubit(qB,candidate2)

            
            # Measure the qubits.
            measured_value = qA.measure()

            with CQCConnection(candidate2) as Bob:
                qB = Bob.recvQubit()
                bob_value = qB.measure()
                assert measured_value + bob_value == 1

            if measured_value == 1:  # `candidate1` is a winner.
                return candidate1
            else:
                return candidate2

    def leader(self):
        assert len(self.queue) >= 2

        winner = self.queue[0]
        
        for i in range(2,len(self.queue) + 1):
            coeff = math.sqrt(1/i)
            winner = self._atomic_flip(winner, self.queue[i - 1], coeff)

        return winner
