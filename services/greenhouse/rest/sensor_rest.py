import cherrypy
import requests
from schemas import Greenhouse, Bed, Sensor


class SensorREST(object):
    def __init__(self):
        pass

    exposed = True

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, greenhouse, bed, **params):
        notfound = True

        # Find user greenhouse the required id
        try:
            gh = Greenhouse.objects.get(id=greenhouse)
        except Exception as e:
            raise cherrypy.HTTPError(404, str(e))

        sensor = Sensor(telemetric=cherrypy.request.json.get('telemetric'))

        uuid = cherrypy.request.json.get('uuid')
        if uuid is not None:
            sensor.uuid = uuid

        # Index the wanted bed
        for idx, bedidx in enumerate(gh.beds):
            if str(bedidx['uuid']) == bed:
                gh.beds[idx].sensors.append(sensor)
                notfound = False

        if notfound is True:
            raise cherrypy.HTTPError(
                404, 'Bed with the uuid ' + bed + ' was not found')

        try:
            gh.save()
        except Exception as e:
            raise cherrypy.HTTPError(400, str(e))

        # Try to delete the sensor from the discover channel
        if uuid is not None:
            try:
                requests.delete("http://discover:5001/api/v1/discover",
                                params={"uuid": uuid},
                                headers={'Accept': 'application/json'})
            except Exception as e:
                print('Problem removing sensor from discover service: ' + str(e))

        cherrypy.response.status = 200
        return {
            "status": 200,
            "data": {
                "greenhouse": {
                    "id": str(gh.id),
                    "location": gh.location,
                    "beds": {
                        "uuid": bed,
                        "sensor": {
                            "uuid": sensor.uuid,
                            "telemetric": sensor.telemetric
                        }
                    }
                }
            }
        }

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, greenhouse, bed, **params):
        notfound_bed, notfound_sensor = True, True
        # Find greenhouse with the required id
        try:
            gh = Greenhouse.objects.get(id=greenhouse)
        except Exception as e:
            raise cherrypy.HTTPError(404, str(e))

        # Index the wanted bed
        for idx1, bedidx in enumerate(gh.beds):
            if str(bedidx['uuid']) == bed:
                notfound_bed = False
                for idx2, sensoridx in enumerate(gh.beds[idx1].sensors):
                    if str(sensoridx['uuid']) == params['uuid']:
                        notfound_sensor = False
                        if cherrypy.request.json.get('telemetric') is not None:
                            gh.beds[idx1].sensors[idx2].telemetric = cherrypy.request.json.get(
                                'telemetric')

        # Raise errors for not found ids
        if notfound_bed is True:
            raise cherrypy.HTTPError(
                404, 'Bed with the uuid ' + bed + ' was not found')

        if notfound_sensor is True:
            raise cherrypy.HTTPError(
                404, 'Sensor with the uuid ' + str(params['uuid']) + ' was not found')

        # Update document on DB
        try:
            gh.save()
        except Exception as e:
            raise cherrypy.HTTPError(404, str(e))

        # Build data
        beds_data = list(map(lambda bed: {
            "uuid": str(bed.uuid),
            "plant": bed.plant,
            "sensors": list(map(lambda s: {
                "uuid": str(s.uuid),
                "telemetric": s.telemetric
            }, bed.sensors))
        }, gh.beds))

        cherrypy.response.status = 200
        return {
            "status": 200,
            "data": {
                "greenhouse": {
                    "id": str(gh.id),
                    "location": gh.location,
                    "beds": beds_data
                }
            }
        }

    @cherrypy.tools.json_out()
    def DELETE(self, greenhouse, bed, **params):
        notfound_bed, notfound_sensor = True, True
        # Find greenhouse with the required id
        try:
            gh = Greenhouse.objects.get(id=greenhouse)
        except Exception as e:
            raise cherrypy.HTTPError(404, str(e))

        # Index the wanted bed
        for idx1, bedidx in enumerate(gh.beds):
            if str(bedidx['uuid']) == bed:
                notfound_bed = False
                for idx2, sensoridx in enumerate(gh.beds[idx1].sensors):
                    if str(sensoridx['uuid']) == params['uuid']:
                        notfound_sensor = False
                        gh.beds[idx1].sensors.pop(idx2)

        # Raise errors for not found ids
        if notfound_bed is True:
            raise cherrypy.HTTPError(
                404, 'Bed with the uuid ' + bed + ' was not found')

        if notfound_sensor is True:
            raise cherrypy.HTTPError(
                404, 'Sensor with the uuid ' + str(params['uuid']) + ' was not found')

        # Update document on DB
        try:
            gh.save()
        except Exception as e:
            raise cherrypy.HTTPError(404, str(e))

        # Build data
        beds_data = list(map(lambda bed: {
            "uuid": str(bed.uuid),
            "plant": bed.plant,
            "sensors": list(map(lambda s: {
                "uuid": str(s.uuid),
                "telemetric": s.telemetric
            }, bed.sensors))
        }, gh.beds))

        cherrypy.response.status = 200
        return {
            "status": 200,
            "data": {
                "greenhouse": {
                    "id": str(gh.id),
                    "location": gh.location,
                    "beds": beds_data
                }
            }
        }
