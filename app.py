from flask import Flask
import turtle_daily
import tick_taker
import alpaca

app = Flask(__name__)

@app.route("/")
def hello():
    return turtle_daily.hello()

@app.route("/last")
def last():
    return turtle_daily.lastEquity()
@app.route("/Ishaan")
def hi():
    return tick_taker.hello()

@app.route("/yo")
def hi1():
    return alpaca.r()

if __name__ == "__main__":
  app.run()