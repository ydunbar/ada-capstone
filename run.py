# followed tutorial by Corey Schafer: https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH&index=1
from app import app

# run without env vars
if __name__ == '__main__':
    app.run(debug=True)