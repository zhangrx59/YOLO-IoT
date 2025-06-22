# coap_server.py
import asyncio, json
from aiocoap import Context, Message, Site, Resource, CHANGED

class Foggy(Resource):
    async def render_post(self, req):
        data = json.loads(req.payload.decode())
        print("CoAP 收到：", data)
        return Message(code=CHANGED)
async def main():
    site = Site()
    site.add_resource(['iot','foggy'], Foggy())
    await Context.create_server_context(site, bind=('::',5683))
    await asyncio.get_running_loop().create_future()
if __name__ == "__main__":
    asyncio.run(main())
