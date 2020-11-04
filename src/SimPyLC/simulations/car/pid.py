# Requirements:
# 1. een stuk code dat aan de hand van 2 inputs een output genereert
# 2. het moet mogelijk zijn om verschillende functies uit te voeren

# Test specificatie
# het sturen van de auto in de simulatie moet stoppen met slingeren
# als de auto visueel niet meer slingert over 5 ronden is de test geslaagd

# Ontwerp
# een class die de verstreken tijd bijhoudt
# de constructor verwacht voor p i en d een functie/constante
# een functie heeft die 2 inputs verwacht en de verstreken tijd deze voert de volgende functies uit:
# een proportionele functie die een output geeft
# een intergratie functie die een output geeft
# een diffrentierende functie die een output geeft
# en voegt de outputs samen tot 1 output


class Pid:

    def __init__(self, p, i, d):
        self.p = p
        self.i = i
        self.d = d
        self.errorIntergral = 0
        self.lastInput = 0

    def control(self, currentInput, expectedInput, dt):
        error = expectedInput - currentInput
        outputP = self.calculateProportional(error)
        outputI = self.calculateIntergational(dt, error)
        outputD = self.calculateDifferentional(currentInput, dt, error)

        output = outputP + outputI + outputD
        self.lastInput = currentInput
        return output

    def calculateProportional(self, error):
        return self.p * error

    def calculateIntergational(self, dt, error):
         self.errorIntergral += self.i * error * dt
         return self.errorIntergral
    
    def calculateDifferentional(self, currentInput, dt, error):
        return  self.d * ((currentInput - self.lastInput )/ dt)


# testPID = Pid(0.1,0.1,0.1)
# output = 0
# for i in range(1,10):
#     output = testPID.control(output, (i * 20), 10)
#     print(f"expected: {i * 20}, output: {output}")

