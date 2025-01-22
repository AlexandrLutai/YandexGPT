from aiohttp import web
import asyncio

async def handle_webhook(request):
    if request.method == 'POST':
        data = await request.json()
        print("received data: ", data)
        # Отправка данных на обработку
        asyncio.create_task(process_data(data))
        return web.Response(text='success', status=200)
    else:
        raise web.HTTPBadRequest()

async def process_data(data):
    # Здесь можно добавить код для обработки данных
    await asyncio.sleep(1)  # Пример асинхронной задачи
    print("processed data: ", data)

app = web.Application()
app.router.add_post('/', handle_webhook)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0')
