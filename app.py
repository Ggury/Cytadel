import flet as fl
import websockets
import json
import asyncio
import httpx

def main(page: fl.Page):
    API_URL = "http://localhost:8000/api/activate-key"
    WS_URL = "ws://localhost:8000/ws/status/"
    
    page.title = "Cytadel Proxy"
    page.window_width = 100
    page.window_height = 100
    page.theme_mode = fl.ThemeMode.DARK


    page.vertical_alignment = fl.MainAxisAlignment.CENTER
    page.horizontal_alignment = fl.CrossAxisAlignment.CENTER


    key_input = fl.TextField(label="Вставьте ваш ключ", password=True, can_reveal_password=True)
    status_label = fl.Text("Статус: Отключено", color="red")
    info_label = fl.Text("")

    async def start_connection(e):
        if not key_input.value: return
        
        status_label.value = "Статус: Ожидание..."
        status_label.color = "orange"
        page.update()

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(API_URL, json={"key": key_input.value})
            
            if resp.status_code != 200:
                status_label.value = f"Ошибка: {resp.status_code}"
                status_label.color = "red"
                page.update()
                return

            data = resp.json()
            user_id = data["user_id"]
            info_label.value = f"Host: {data['host']}\nPort: {data['port']}"

            async with websockets.connect(f"{WS_URL}{user_id}") as ws:
                async for msg in ws:
                    res = json.loads(msg)
                    if res["status"] == "connected":
                        status_label.value = "Статус: Подключено"
                        status_label.color = "green"
                    else:
                        status_label.value = "Статус: Отключено"
                        status_label.color = "red"
                    page.update()
        except Exception as ex:
            status_label.value = "Ошибка соединения"
            page.update()

    page.add(
        fl.Column([
            fl.Text("Cytadel Proxy", size=25),
            key_input,
            fl.ElevatedButton("Подключиться", on_click=start_connection),
            status_label,
            info_label
        ], horizontal_alignment=fl.CrossAxisAlignment.CENTER)
    )

fl.app(target=main)