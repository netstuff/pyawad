import os
import json
import asyncio
import aio_pika
import datetime
from dateutil.parser import parse

from pyawad.request import RouteRequest, FareRequest, RequestException


RABBIT_URL = 'amqp://data:passx@127.0.0.1:5672'
REQUEST_QUEUE_NAME = os.environ.get('AMPQ-QUEUE-REQUEST', 'route-request')
RESPONSE_QUEUE_NAME = os.environ.get('AMPQ-QUEUE-RESPONSE', 'route-response')


async def main(loop):
    connection = await aio_pika.connect_robust(RABBIT_URL, loop=loop)

    async with connection:
        # Creating channel
        channel = await connection.channel()

        # Declaring queue
        queue = await channel.declare_queue(
            REQUEST_QUEUE_NAME,
            durable=True,
            auto_delete=False
        )

        await channel.declare_queue(
            RESPONSE_QUEUE_NAME,
            durable=True,
            auto_delete=False
        )

        print('Connected to {0} ({1}).'.format(RABBIT_URL, REQUEST_QUEUE_NAME))

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    query = json.loads(message.body)
                    task_response = {
                        'status': None,
                        'task_id': query['task_id'],
                        'result': {
                            'fares': [],
                            'routes': [],
                        },
                    }

                    print('Got a task: {city_from} ({date_from}) — {city_to} ({date_till})'.format(**query))

                    query_there = {
                        'date': parse(query.get('date_from')),
                        'departure': query.get('city_from'),
                        'arrival': query.get('city_to'),
                    }

                    query_back = {
                        'date': parse(query.get('date_till')),
                        'departure': query.get('city_to'),
                        'arrival': query.get('city_from'),
                    }

                    # Get fares data and prepare response.
                    for query in [query_there, query_back]:
                        route = RouteRequest(**query)

                        await route.create()
                        print('Route created: {0.uid}'.format(route))

                        # Add route data to response.
                        task_response['result']['routes'].append(route.to_dict())

                        async for fare in route.find_fares():
                            task_response['result']['fares'].append(fare.to_dict())

                result = json.dumps(task_response).encode('utf8')
                task_response['status'] = 'ok'

                # Publish results to response task.
                await channel.default_exchange.publish(
                    aio_pika.Message(body=result),
                    routing_key=RESPONSE_QUEUE_NAME,
                )

                print('Result with {0} fares is sent'.format(len(task_response['result']['fares'])))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

    print('Connection closed.')
