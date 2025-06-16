FROM node:18-alpine

WORKDIR /app

# Copy and build everything
COPY . .

# Install backend deps
WORKDIR /app/backend
RUN npm install

# Install and build frontend
WORKDIR /app/frontend
RUN npm install && npm run build

# Create simple server
WORKDIR /app
RUN echo 'const express = require("express");\n\
const path = require("path");\n\
const app = express();\n\
app.use(express.static(path.join(__dirname, "frontend/build")));\n\
app.get("/health", (req, res) => res.json({status: "ok"}));\n\
app.get("*", (req, res) => {\n\
  res.sendFile(path.join(__dirname, "frontend/build", "index.html"));\n\
});\n\
const PORT = process.env.PORT || 3000;\n\
app.listen(PORT, () => console.log(`Server on port ${PORT}`));' > simple-server.js

EXPOSE 3000

CMD ["node", "simple-server.js"]