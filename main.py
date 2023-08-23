from fastapi import FastAPI
from v1.routers import droppers, doses
# import uvicorn

app = FastAPI()
app.title = "Drops Manager"
app.version = "1.0.2"
app.description = "Eye drop manager platform that allows users to keep track of their daily doses, reminders between hours and track the number of drops used."

# Routers
app.include_router(droppers.router)
app.include_router(doses.router)

@app.get("/")
async def root():
    return "Drops Manager API - Go to ~ /docs ~ or ~ /redoc ~ to explore every avaliable endpoint."

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000,  log_level="debug", reload= True)