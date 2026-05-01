import flet as fl
import websockets
import json
import asyncio
def main(page: fl.Page):
    # Теперь URL чистый, без ID в конце
    WS_URL = "ws://localhost:8000/ws/status/" 
    
    page.title = "Cytadel Proxy"
    page.window_width = 400
    page.window_height = 450
    page.theme_mode = fl.ThemeMode.DARK

    # Поле только для ключа
    activation_key_field = fl.TextField(
        label="Ключ активации", 
        text_align=fl.TextAlign.CENTER,
        password=True, 
        can_reveal_password=True
    )
    status_text = fl.Text("Статус: Отключено", color="red", size=16)

    async def connect_ws_task(activation_key):
        try:
            async with websockets.connect(WS_URL) as websocket:
                # Просто шлем ключ. Сервер сам поймет, кто мы.
                await websocket.send(json.dumps({"key": activation_key}))
                
                response = await websocket.recv()
                data = json.loads(response)

                if data["status"] == "connected":
                    status_text.value = f"Подключено: {data['host']}:{data['port']}"
                    status_text.color = "green"
                    page.update()
                    while True: await asyncio.sleep(1)
                else:
                    status_text.value = f"Ошибка: {data.get('message')}"
                    status_text.color = "red"
                    page.update()
        except:
            status_text.value = "Ошибка соединения"
            status_text.color = "red"
            page.update()

    def on_connect(e):
        page.run_task(connect_ws_task, activation_key_field.value)

    page.add(
        fl.Column([
            fl.Icon(fl.icons.Icons.SHIELD_OUTLINED, size=50, color="blue"),
            fl.Text("Cytadel Activation", size=20),
            activation_key_field,
            fl.ElevatedButton("Активировать", on_click=on_connect, width=200),
            status_text
        ], horizontal_alignment=fl.CrossAxisAlignment.CENTER, spacing=20)
    )

fl.app(target=main)