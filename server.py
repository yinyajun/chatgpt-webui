import model
import gradio_ui
import uvicorn
import fastapi
import gradio as gr
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

app = fastapi.FastAPI()
templates = Jinja2Templates(directory="templates")

# gradio web ui
app = gr.mount_gradio_app(app=app,
                          path="/gradio_ui",
                          blocks=gradio_ui.create_ui().queue(concurrency_count=5, max_size=64))


# web ui using SSE protocol
@app.get("/web_ui")
def index(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/stream")
async def stream(request: fastapi.Request):
    query = request.query_params.get("query", "")
    session_id = request.query_params.get("session_id", "default")
    return EventSourceResponse(model.ChatGPT().stream_chat(query, session_id))


if __name__ == '__main__':
    uvicorn.run(app)
