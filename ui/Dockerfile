FROM node:20-bullseye

WORKDIR /app

# Kopiere package.json und package-lock.json getrennt für klareres Layering
COPY package.json package-lock.json* ./

# Installiere Abhängigkeiten
RUN npm ci

# Danach alles kopieren (Source Code)
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
