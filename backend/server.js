require("dotenv").config();

const express = require("express");
const diseasesRoutes = require("./routes/diseases");
const userRoutes = require("./routes/user");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

// Enable CORS first
app.use(
  cors({
    origin: "http://localhost:3000",
    credentials: true,
  })
);

app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  console.log(req.path, req.method);
  next();
});

// Routes
app.use("/api/diseases", diseasesRoutes);
app.use("/api/user", userRoutes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: "Something went wrong!" });
});

// connect to db
mongoose.set("strictQuery", false);
mongoose
  .connect(process.env.MONGO_URL)
  .then(() => {
    app.listen(process.env.PORT, () => {
      console.log("Connected to db and Listening on port", process.env.PORT);
    });
  })
  .catch((err) => {
    console.error("Database connection error:", err);
  });
