# Gebruik een lichte Python versie
FROM python:3.9-slim

# Zet de werkmap in de container
WORKDIR /app

# Installeer Flask (en andere packages indien nodig)
RUN pip install flask

# Kopieer jouw bestanden (app.py, templates map, static map, database) naar de container
COPY . .

# Zorg dat de database map schrijfbaar is (belangrijk voor SQLite!)
RUN chmod -R 777 .

# Start de applicatie (zorg dat app.py op host 0.0.0.0 draait, zie tip onderaan)
CMD ["python", "app.py"]