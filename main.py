import UserInterface
from fastapi import FastAPI

app = FastAPI()
totalEnergy = 0 # units are kWh


@app.get('/')
def root():
    return totalEnergy

if __name__ == "__main__":
    UserInterface.init(app)

