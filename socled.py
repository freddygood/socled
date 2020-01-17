from flask import Flask, Response, request, abort
from flask_caching import Cache
from subprocess import check_output

application = Flask(__name__)
cache = Cache(application, config={'CACHE_TYPE': 'simple'})

import config

host = getattr(config, 'host', '127.0.0.1')
port = getattr(config, 'port', 8080)
debug = getattr(config, 'debug', True)
cache_timeout = getattr(config, 'cache_timeout', 5)

thumbnails_url = getattr(config, 'thumbnails_url', 'http://localhost')


def get_thumbnail(app, stream):
	ffmpeg_line = 'ffmpeg -loglevel error -i \"{}/{}/{}/playlist.m3u8\" -qscale:v 2 -frames:v 1 -f singlejpeg -'.format(thumbnails_url, app, stream)
	application.logger.warning('ffmpeg getting image line is {}'.format(ffmpeg_line))
	return check_output(ffmpeg_line, shell = True, env = {"AV_LOG_FORCE_NOCOLOR": "true"})


@application.route('/')
def index():
	abort(404)


@application.route('/transcoderthumbnail', methods=['GET'])
@cache.cached(timeout=cache_timeout, query_string = True)
def transcoder_thumbnail():

	app = request.args.get('application', default = '', type = str)
	stream = request.args.get('streamname', default = '', type = str)
	format = request.args.get('format', default = 'jpeg', type = str)
	size = request.args.get('size', default = '4x3', type = str)
	expires = request.args.get('expires', default = '30', type = int)

	try:
		assert app and stream, 'Neither application nor streamname was passed'
	except Exception as e:
		application.logger.error(e.message, exc_info=True)
		abort(502)

	try:
		data = get_thumbnail(app, stream)
	except Exception as e:
		application.logger.error(e.message, exc_info=True)
		abort(502)

	response = Response(data)
	response.status_code = 200
	response.mimetype='image/jpeg'
	response.cache_control.max_age = expires
	response.cache_control.public = True

	return response


if __name__ == "__main__":
	application.run(debug=debug, host=host, port=port)
