
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .middleware import RealTimeMonitorMiddleware
from fastapi.responses import HTMLResponse
from .redis_client import redis_client
from contextlib import asynccontextmanager, suppress
from .database import engine, Base, AsyncSessionLocal, MetricSnapshot
from pathlib import Path
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import chronexis
import os



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db_sync_task = asyncio.create_task(sync_metrics_to_postgres())
    yield

    db_sync_task.cancel()
    with suppress(asyncio.CancelledError):
        await db_sync_task

app = FastAPI(title="ZA0 Live-Monitor", lifespan=lifespan)

chronexis.install(
    app,
    api_key=os.environ["CHRONEXIS_API_KEY"],
    endpoint="https://chronexis.dedyn.io/v1/traces",
    on_drop=lambda reason, payload: print(f"[chronexis] DROPPED: {reason}"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RealTimeMonitorMiddleware)

async def sync_metrics_to_postgres():
    while True:
        try:
            await asyncio.sleep(10)

            active_connections = await redis_client.get("active_connections") or "0"
            total_requests = await redis_client.get("total_requests") or "0"
            latencies = await redis_client.lrange("request_times", 0, -1)
            average_latency = 0.0

            if latencies:
                average_latency = sum(float(latency) for latency in latencies) / len(latencies)

            async with AsyncSessionLocal() as session:
                snapshot = MetricSnapshot(
                    active_connections=int(active_connections),
                    total_requests=int(total_requests),
                    average_latency=(round(average_latency, 2))
                )
                session.add(snapshot)
                await session.commit()
            print(f"Metrics snapshot saved to PostgreSQL: {snapshot}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error syncing metrics to PostgreSQL: {e}")
                
        

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            active_connections = await redis_client.get("active_connections") or "0"
            total_requests = await redis_client.get("total_requests") or "0"
            
            latencies = await redis_client.lrange("request_times", 0, -1)
            average_latency = 0.0
            if latencies:
                average_latency = sum(float(latency) for latency in latencies) / len(latencies)

            data = {
                "active_connections": int(active_connections),
                "total_requests": int(total_requests),
                "average_latency": round(average_latency, 2)
            }

            await websocket.send_json(data)
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print("client disconnected")


@app.get("/api/v1/fast-task")
async def fast_task():
    return {"status":"success", "type":"fast"}

@app.get("/api/v1/slow-task")
async def slow_task():
    await asyncio.sleep(0.3)
    return {"status":"success", "type":"slow"}

@app.get("/api/v1/latency-report")
async def latency_report():
    latencies = await redis_client.lrange("request_times", 0, -1)
    values = [float(latency) for latency in latencies]
    slow = [value for value in values if value > 1000]
    worst = max(slow)
    return {
        "worst_ms": round(worst, 2),
        "slow_count": len(slow),
        "sampled": len(values),
    }

@app.get("/api/v1/connections/ratio")
async def connections_ratio():
    active_connections = await redis_client.get("active_connections") or "0"
    total_requests = await redis_client.get("total_requests") or "0"
    ratio = int(active_connections) / int(total_requests)
    return {
        "active": int(active_connections),
        "total": int(total_requests),
        "ratio_pct": round(ratio * 100, 2),
    }

@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    template_path = Path(__file__).resolve().parent / "templates" / "index.html"
    return template_path.read_text(encoding="utf-8")
